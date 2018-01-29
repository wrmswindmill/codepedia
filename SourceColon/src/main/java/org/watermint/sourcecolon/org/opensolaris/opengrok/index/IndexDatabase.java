/*
 * CDDL HEADER START
 *
 * The contents of this file are subject to the terms of the
 * Common Development and Distribution License (the "License").
 * You may not use this file except in compliance with the License.
 *
 * See LICENSE.txt included in this distribution for the specific
 * language governing permissions and limitations under the License.
 *
 * When distributing Covered Code, include this CDDL HEADER in each
 * file and include the License file at LICENSE.txt.
 * If applicable, add the following below this CDDL HEADER, with the
 * fields enclosed by brackets "[]" replaced with your own identifying
 * information: Portions Copyright [yyyy] [name of copyright owner]
 *
 * CDDL HEADER END
 */

/*
 * Copyright (c) 2008, 2010, Oracle and/or its affiliates. All rights reserved.
 * Portions Copyright (c) 2013 Takayuki Okazaki.
 */

package org.watermint.sourcecolon.org.opensolaris.opengrok.index;

import org.apache.lucene.document.DateTools;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Fieldable;
import org.apache.lucene.index.*;
import org.apache.lucene.queryParser.ParseException;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.search.spell.LuceneDictionary;
import org.apache.lucene.search.spell.SpellChecker;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.store.LockFactory;
import org.apache.lucene.store.NoLockFactory;
import org.apache.lucene.store.SimpleFSLockFactory;
import org.apache.lucene.util.Version;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.AnalyzerGuru;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.Ctags;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.Definitions;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.FileAnalyzer;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.FileAnalyzer.Genre;
import org.watermint.sourcecolon.org.opensolaris.opengrok.configuration.Project;
import org.watermint.sourcecolon.org.opensolaris.opengrok.configuration.RuntimeEnvironment;
import org.watermint.sourcecolon.org.opensolaris.opengrok.search.QueryBuilder;
import org.watermint.sourcecolon.org.opensolaris.opengrok.web.Util;

import java.io.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * This class is used to create / update the index databases. Currently we use
 * one index database per project.
 *
 * @author Trond Norbye
 * @author Lubos Kosco , update for lucene 3.0.0
 */
public class IndexDatabase {

    private Project project;
    private FSDirectory indexDirectory;
    private FSDirectory spellDirectory;
    private IndexWriter writer;
    private TermEnum termEnum;
    private IgnoredNames ignoredNames;
    private Filter includedNames;
    private AnalyzerGuru analyzerGuru;
    private File xrefDir;
    private List<IndexChangedListener> listeners;
    private final Object lock = new Object();
    private boolean running;
    private List<String> directories;
    private static final Logger log = Logger.getLogger(IndexDatabase.class.getName());
    private Ctags ctags;
    private LockFactory lockFactory;

    /**
     * Create a new instance of the Index Database. Use this constructor if
     * you don't use any projects
     *
     * @throws IOException if an error occurs while creating directories
     */
    public IndexDatabase() throws IOException {
        this(null);
    }

    /**
     * Create a new instance of an Index Database for a given project
     *
     * @param project the project to create the database for
     * @throws IOException if an error occurs while creating directories
     */
    public IndexDatabase(Project project) throws IOException {
        this.project = project;
        lockFactory = new SimpleFSLockFactory();
        initialize();
    }

    /**
     * Update the index database for all of the projects
     *
     * @param executor An executor to run the job
     * @param listener where to signal the changes to the database
     * @throws IOException if an error occurs
     */
    static void updateAll(ExecutorService executor, IndexChangedListener listener) throws IOException {
        RuntimeEnvironment env = RuntimeEnvironment.getInstance();
        List<IndexDatabase> dbs = new ArrayList<>();

        if (env.hasProjects()) {
            for (Project project : env.getProjects()) {
                dbs.add(new IndexDatabase(project));
            }
        } else {
            dbs.add(new IndexDatabase());
        }

        for (IndexDatabase d : dbs) {
            final IndexDatabase db = d;
            d.updateTimestamp();
            if (listener != null) {
                db.addIndexChangedListener(listener);
            }

            executor.submit(new Runnable() {

                @Override
                public void run() {
                    try {
                        db.update();
                    } catch (Throwable e) {
                        log.log(Level.SEVERE, "Problem updating lucene index database: ", e);
                    }
                }
            });
        }
    }

    @SuppressWarnings("PMD.CollapsibleIfStatements")
    private void initialize() throws IOException {
        synchronized (this) {
            RuntimeEnvironment env = RuntimeEnvironment.getInstance();
            File indexDir = new File(env.getDataRootFile(), "index");
            File spellDir = new File(env.getDataRootFile(), "spellIndex");
            if (project != null) {
                indexDir = new File(indexDir, project.getPath());
                spellDir = new File(spellDir, project.getPath());
            }

            if (!indexDir.exists() && !indexDir.mkdirs()) {
                // to avoid race conditions, just recheck..
                if (!indexDir.exists()) {
                    throw new FileNotFoundException("Failed to create root directory [" + indexDir.getAbsolutePath() + "]");
                }
            }

            if (!spellDir.exists() && !spellDir.mkdirs()) {
                if (!spellDir.exists()) {
                    throw new FileNotFoundException("Failed to create root directory [" + spellDir.getAbsolutePath() + "]");
                }
            }

            if (!env.isUsingLuceneLocking()) {
                lockFactory = NoLockFactory.getNoLockFactory();
            }
            indexDirectory = FSDirectory.open(indexDir, lockFactory);
            spellDirectory = FSDirectory.open(spellDir, lockFactory);
            ignoredNames = env.getIgnoredNames();
            includedNames = env.getIncludedNames();
            analyzerGuru = new AnalyzerGuru();
            if (env.isGenerateHtml()) {
                xrefDir = new File(env.getDataRootFile(), "xref");
            }
            listeners = new ArrayList<>();
            directories = new ArrayList<>();
            updateTimestamp();
        }
    }

    /**
     * By default the indexer will traverse all directories in the project.
     * If you add directories with this function update will just process
     * the specified directories.
     *
     * @param dir The directory to scan
     * @return <code>true</code> if the file is added, false oth
     */
    @SuppressWarnings("PMD.UseStringBufferForStringAppends")
    public boolean addDirectory(String dir) {
        String directory = dir;
        if (directory.startsWith("\\")) {
            directory = directory.replace('\\', '/');
        } else if (directory.charAt(0) != '/') {
            directory = "/" + directory;
        }
        File file = new File(RuntimeEnvironment.getInstance().getSourceRootFile(), directory);
        if (file.exists()) {
            directories.add(directory);
            return true;
        }
        return false;
    }

    /**
     * Update the content of this index database
     *
     * @throws IOException if an error occurs
     */
    public void update() throws IOException {
        synchronized (lock) {
            if (running) {
                throw new IOException("Indexer already running!");
            }
            running = true;
        }

        String ctgs = RuntimeEnvironment.getInstance().getCtags();
        if (ctgs != null) {
            ctags = new Ctags();
            ctags.setBinary(ctgs);
        }
        if (ctags == null) {
            log.severe("Unable to run ctags! searching definitions will not work!");
        }

        try {
            writer = new IndexWriter(indexDirectory, new IndexWriterConfig(Version.LUCENE_36, AnalyzerGuru.getAnalyzer()));
            writer.commit();
            if (directories.isEmpty()) {
                if (project == null) {
                    directories.add("");
                } else {
                    directories.add(project.getPath());
                }
            }

            for (String dir : directories) {
                File sourceRoot;
                if ("".equals(dir)) {
                    sourceRoot = RuntimeEnvironment.getInstance().getSourceRootFile();
                } else {
                    sourceRoot = new File(RuntimeEnvironment.getInstance().getSourceRootFile(), dir);
                }

                String startUid = Util.path2uid(dir, "");

                try (IndexReader reader = IndexReader.open(indexDirectory)) {
                    termEnum = reader.terms(new Term("u", startUid)); // init uid iterator

                    //TODO below should be optional, since it traverses the tree once more to get total count! :(
                    int file_cnt = 0;
                    if (RuntimeEnvironment.getInstance().isPrintProgress()) {
                        log.log(Level.INFO, "Counting files in {0} ...", dir);
                        file_cnt = indexDown(sourceRoot, dir, true, 0, 0);
                        if (log.isLoggable(Level.INFO)) {
                            log.log(Level.INFO, "Need to process: {0} files for {1}", new Object[]{file_cnt, dir});
                        }
                    }

                    indexDown(sourceRoot, dir, false, 0, file_cnt);

                    while (termEnum.term() != null && termEnum.term().field().equals("u") && termEnum.term().text().startsWith(startUid)) {
                        removeFile();
                        termEnum.next();
                    }
                }
            }
        } finally {
            if (writer != null) {
                try {
                    writer.close();
                } catch (IOException e) {
                    log.log(Level.WARNING, "An error occurred while closing writer", e);
                }
            }

            if (ctags != null) {
                ctags.close();
            }

            synchronized (lock) {
                running = false;
            }
        }

        createSpellingSuggestions();
        updateTimestamp();
    }

    public void updateTimestamp() {
        RuntimeEnvironment env = RuntimeEnvironment.getInstance();
        File timestamp = new File(env.getDataRootFile(), "timestamp");
        if (timestamp.exists()) {
            if (!timestamp.setLastModified(System.currentTimeMillis())) {
                log.log(Level.WARNING, "Failed to set last modified time on ''{0}'', used for time-stamping the index database.", timestamp.getAbsolutePath());
            }
        } else {
            try {
                if (!timestamp.createNewFile()) {
                    log.log(Level.WARNING, "Failed to create file ''{0}'', used for time-stamping the index database.", timestamp.getAbsolutePath());
                }
            } catch (IOException e) {
                log.log(Level.WARNING, "Failed to create file ''{0}'', used for time-stamping the index database.", timestamp.getAbsolutePath());
            }
        }
    }

    /**
     * Generate a spelling suggestion for the definitions stored in defs
     */
    public void createSpellingSuggestions() {
        IndexReader indexReader = null;
        SpellChecker checker = null;

        try {
            log.info("Generating spelling suggestion index ... ");
            indexReader = IndexReader.open(indexDirectory);
            checker = new SpellChecker(spellDirectory);
            //TODO below seems only to index "defs" , possible bug ?
            checker.indexDictionary(new LuceneDictionary(indexReader, "defs"), new IndexWriterConfig(Version.LUCENE_36, null), true);
            log.info("done");
        } catch (IOException e) {
            log.log(Level.SEVERE, "ERROR: Generating spelling: {0}", e);
        } finally {
            if (indexReader != null) {
                try {
                    indexReader.close();
                } catch (IOException e) {
                    log.log(Level.WARNING, "An error occurred while closing reader", e);
                }
            }
            if (spellDirectory != null) {
                spellDirectory.close();
            }
        }
    }

    /**
     * Remove a stale file (termEnum.term().text()) from the index database
     * (and the xref file)
     *
     * @throws IOException if an error occurs
     */
    private void removeFile() throws IOException {
        String path = Util.uid2url(termEnum.term().text());

        for (IndexChangedListener listener : listeners) {
            listener.fileRemove(path);
        }
        writer.deleteDocuments(termEnum.term());

        File xrefFile;
        if (RuntimeEnvironment.getInstance().isCompressXref()) {
            xrefFile = new File(xrefDir, path + ".gz");
        } else {
            xrefFile = new File(xrefDir, path);
        }
        File parent = xrefFile.getParentFile();

        if (!xrefFile.delete() && xrefFile.exists()) {
            log.log(Level.INFO, "Failed to remove obsolete xref-file: {0}", xrefFile.getAbsolutePath());
        }

        // Remove the parent directory if it's empty
        if (parent.delete()) {
            log.log(Level.FINE, "Removed empty xref dir:{0}", parent.getAbsolutePath());
        }
        for (IndexChangedListener listener : listeners) {
            listener.fileRemoved(path);
        }
    }

    /**
     * Add a file to the Lucene index (and generate a xref file)
     *
     * @param file The file to add
     * @param path The path to the file (from source root)
     * @throws IOException if an error occurs
     */
    private void addFile(File file, String path) throws IOException {
        try (InputStream in = new BufferedInputStream(new FileInputStream(file))) {
            FileAnalyzer fa = AnalyzerGuru.getAnalyzer(in, path);
            for (IndexChangedListener listener : listeners) {
                listener.fileAdd(path, fa.getClass().getSimpleName());
            }
            fa.setCtags(ctags);
            fa.setProject(Project.getProject(path));

            Document d;
            try {
                d = analyzerGuru.getDocument(file, in, path, fa);
            } catch (Exception e) {
                log.log(Level.INFO, "Skipped file ''{0}'' because the analyzer didn''t " + "understand it.", path);
                log.log(Level.FINE, "Exception from analyzer:", e);
                return;
            }

            writer.addDocument(d, fa);
            Genre g = fa.getFactory().getGenre();
            if (xrefDir != null && (g == Genre.PLAIN || g == Genre.XREFABLE)) {
                File xrefFile = new File(xrefDir, path);
                // If mkdirs() returns false, the failure is most likely
                // because the file already exists. But to check for the
                // file first and only add it if it doesn't exists would
                // only increase the file IO...
                if (!xrefFile.getParentFile().mkdirs()) {
                    assert xrefFile.getParentFile().exists();
                }
                fa.writeXref(xrefDir, path);
            }
            for (IndexChangedListener listener : listeners) {
                listener.fileAdded(path, fa.getClass().getSimpleName());
            }
        }

    }

    /**
     * Check if I should accept this file into the index database
     *
     * @param file the file to check
     * @return true if the file should be included, false otherwise
     */
    private boolean accept(File file) {

        if (!includedNames.isEmpty() &&
                // the filter should not affect directory names
                (!(file.isDirectory() || includedNames.match(file)))) {
            return false;
        }
        if (ignoredNames.ignore(file)) {
            return false;
        }

        String absolutePath = file.getAbsolutePath();

        if (!file.canRead()) {
            log.log(Level.WARNING, "Warning: could not read {0}", absolutePath);
            return false;
        }

        try {
            String canonicalPath = file.getCanonicalPath();
            if (!absolutePath.equals(canonicalPath) && !acceptSymlink(absolutePath, canonicalPath)) {
                log.log(Level.FINE, "Skipped symlink ''{0}'' -> ''{1}''", new Object[]{absolutePath, canonicalPath});
                return false;
            }
            //below will only let go files and directories, anything else is considered special and is not added
            if (!file.isFile() && !file.isDirectory()) {
                log.log(Level.WARNING, "Warning: ignored special file {0}", absolutePath);
                return false;
            }
        } catch (IOException exp) {
            log.log(Level.WARNING, "Warning: Failed to resolve name: {0}", absolutePath);
            log.log(Level.FINE, "Stack Trace: ", exp);
        }

        if (file.isDirectory()) {
            // always accept directories so that their files can be examined
            return true;
        }

        // this is an unversioned file, check if it should be indexed
        return !RuntimeEnvironment.getInstance().isIndexVersionedFilesOnly();
    }

    boolean accept(File parent, File file) {
        try {
            File f1 = parent.getCanonicalFile();
            File f2 = file.getCanonicalFile();
            if (f1.equals(f2)) {
                log.log(Level.INFO, "Skipping links to itself...: {0} {1}", new Object[]{parent.getAbsolutePath(), file.getAbsolutePath()});
                return false;
            }

            // Now, let's verify that it's not a link back up the chain...
            File t1 = f1;
            while ((t1 = t1.getParentFile()) != null) {
                if (f2.equals(t1)) {
                    log.log(Level.INFO, "Skipping links to parent...: {0} {1}", new Object[]{parent.getAbsolutePath(), file.getAbsolutePath()});
                    return false;
                }
            }

            return accept(file);
        } catch (IOException ex) {
            log.log(Level.WARNING, "Warning: Failed to resolve name: {0} {1}", new Object[]{parent.getAbsolutePath(), file.getAbsolutePath()});
        }
        return false;
    }

    /**
     * Check if I should accept the path containing a symlink
     *
     * @param absolutePath  the path with a symlink to check
     * @param canonicalPath the canonical path to the file
     * @return true if the file should be accepted, false otherwise
     */
    private boolean acceptSymlink(String absolutePath, String canonicalPath) throws IOException {
        // Always accept local symlinks
        if (isLocal(canonicalPath)) {
            return true;
        }

        for (String allowedSymlink : RuntimeEnvironment.getInstance().getAllowedSymlinks()) {
            if (absolutePath.startsWith(allowedSymlink)) {
                String allowedTarget = new File(allowedSymlink).getCanonicalPath();
                if (canonicalPath.startsWith(allowedTarget) && absolutePath.substring(allowedSymlink.length()).equals(canonicalPath.substring(allowedTarget.length()))) {
                    return true;
                }
            }
        }
        return false;
    }

    /**
     * Check if a file is local to the current project. If we don't have
     * projects, check if the file is in the source root.
     *
     * @param path the path to a file
     * @return true if the file is local to the current repository
     */
    private boolean isLocal(String path) {
        RuntimeEnvironment env = RuntimeEnvironment.getInstance();
        String srcRoot = env.getSourceRootPath();

        boolean local = false;

        if (path.startsWith(srcRoot)) {
            if (env.hasProjects()) {
                String relPath = path.substring(srcRoot.length());
                if (project.equals(Project.getProject(relPath))) {
                    // File is under the current project, so it's local.
                    local = true;
                }
            } else {
                // File is under source root, and we don't have projects, so
                // consider it local.
                local = true;
            }
        }

        return local;
    }

    /**
     * Generate indexes recursively
     *
     * @param dir        the root indexDirectory to generate indexes for
     * @param parent     parent
     * @param count_only if true will just traverse the source root and count files
     * @param cur_count  current count during the traversal of the tree
     * @param est_total  estimate total files to process
     */
    private int indexDown(File dir, String parent, boolean count_only, int cur_count, int est_total) throws IOException {
        int lcur_count = cur_count;

        if (!accept(dir)) {
            return lcur_count;
        }

        File[] files = dir.listFiles();
        if (files == null) {
            log.log(Level.SEVERE, "Failed to get file listing for: {0}", dir.getAbsolutePath());
            return lcur_count;
        }
        Arrays.sort(files, new Comparator<File>() {
            @Override
            public int compare(File p1, File p2) {
                return p1.getName().compareTo(p2.getName());
            }
        });

        for (File file : files) {
            if (accept(dir, file)) {
                String path = parent + '/' + file.getName();

                if (file.isDirectory()) {
                    lcur_count = indexDown(file, path, count_only, lcur_count, est_total);
                } else {
                    lcur_count++;
                    if (count_only) {
                        continue;
                    }

                    if (RuntimeEnvironment.getInstance().isPrintProgress() && est_total > 0 && log.isLoggable(Level.INFO)) {
                        log.log(Level.INFO, "Progress: {0} ({1}%)", new Object[]{lcur_count, (lcur_count * 100.0f / est_total)});
                    }

                    if (termEnum != null) {
                        String uid = Util.path2uid(path, DateTools.timeToString(file.lastModified(), DateTools.Resolution.MILLISECOND)); // construct uid for doc
                        while (termEnum.term() != null && termEnum.term().field().equals("u") &&
                                termEnum.term().text().compareTo(uid) < 0) {
                            removeFile();
                            termEnum.next();
                        }

                        if (termEnum.term() != null && termEnum.term().field().equals("u") &&
                                termEnum.term().text().compareTo(uid) == 0) {
                            termEnum.next(); // keep matching docs
                            continue;
                        }
                    }
                    try {
                        addFile(file, path);
                    } catch (Exception e) {
                        log.log(Level.WARNING, "Failed to add file " + file.getAbsolutePath(), e);
                    }
                }
            }
        }

        return lcur_count;
    }

    /**
     * Register an object to receive events when modifications is done to the
     * index database.
     *
     * @param listener the object to receive the events
     */
    public void addIndexChangedListener(IndexChangedListener listener) {
        listeners.add(listener);
    }

    /**
     * Remove an object from the lists of objects to receive events when
     * modifications is done to the index database
     *
     * @param listener the object to remove
     */
    public void removeIndexChangedListener(IndexChangedListener listener) {
        listeners.remove(listener);
    }

    /**
     * List all files in all of the index databases
     *
     * @throws IOException if an error occurs
     */
    public static void listAllFiles() throws IOException {
        listAllFiles(null);
    }

    /**
     * List all files in some of the index databases
     *
     * @param subFiles Subdirectories for the various projects to list the files
     *                 for (or null or an empty list to dump all projects)
     * @throws IOException if an error occurs
     */
    public static void listAllFiles(List<String> subFiles) throws IOException {
        RuntimeEnvironment env = RuntimeEnvironment.getInstance();
        if (env.hasProjects()) {
            if (subFiles == null || subFiles.isEmpty()) {
                for (Project project : env.getProjects()) {
                    IndexDatabase db = new IndexDatabase(project);
                    db.listFiles();
                }
            } else {
                for (String path : subFiles) {
                    Project project = Project.getProject(path);
                    if (project == null) {
                        log.log(Level.WARNING, "Warning: Could not find a project for \"{0}\"", path);
                    } else {
                        IndexDatabase db = new IndexDatabase(project);
                        db.listFiles();
                    }
                }
            }
        } else {
            IndexDatabase db = new IndexDatabase();
            db.listFiles();
        }
    }

    /**
     * List all of the files in this index database
     *
     * @throws IOException If an IO error occurs while reading from the database
     */
    public void listFiles() throws IOException {
        IndexReader indexReader = null;
        TermEnum termEnum = null;

        try {
            indexReader = IndexReader.open(indexDirectory); // open existing index
            termEnum = indexReader.terms(new Term("u", "")); // init uid iterator
            while (termEnum.term() != null) {
                log.fine(Util.uid2url(termEnum.term().text()));
                termEnum.next();
            }
        } finally {
            if (termEnum != null) {
                try {
                    termEnum.close();
                } catch (IOException e) {
                    log.log(Level.WARNING, "An error occurred while closing index iterator", e);
                }
            }

            if (indexReader != null) {
                try {
                    indexReader.close();
                } catch (IOException e) {
                    log.log(Level.WARNING, "An error occurred while closing index reader", e);
                }
            }
        }
    }

    static void listFrequentTokens() throws IOException {
        listFrequentTokens(null);
    }

    static void listFrequentTokens(List<String> subFiles) throws IOException {
        final int limit = 4;

        RuntimeEnvironment env = RuntimeEnvironment.getInstance();
        if (env.hasProjects()) {
            if (subFiles == null || subFiles.isEmpty()) {
                for (Project project : env.getProjects()) {
                    IndexDatabase db = new IndexDatabase(project);
                    db.listTokens(4);
                }
            } else {
                for (String path : subFiles) {
                    Project project = Project.getProject(path);
                    if (project == null) {
                        log.log(Level.WARNING, "Warning: Could not find a project for \"{0}\"", path);
                    } else {
                        IndexDatabase db = new IndexDatabase(project);
                        db.listTokens(4);
                    }
                }
            }
        } else {
            IndexDatabase db = new IndexDatabase();
            db.listTokens(limit);
        }
    }

    public void listTokens(int freq) throws IOException {
        IndexReader indexReader = null;
        TermEnum termEnum = null;

        try {
            indexReader = IndexReader.open(indexDirectory);
            termEnum = indexReader.terms(new Term("defs", ""));
            while (termEnum.term() != null) {
                if (termEnum.term().field().startsWith("f")) {
                    if (termEnum.docFreq() > 16 && termEnum.term().text().length() > freq) {
                        log.warning(termEnum.term().text());
                    }
                    termEnum.next();
                } else {
                    break;
                }
            }
        } finally {
            if (termEnum != null) {
                try {
                    termEnum.close();
                } catch (IOException e) {
                    log.log(Level.WARNING, "An error occurred while closing index iterator", e);
                }
            }

            if (indexReader != null) {
                try {
                    indexReader.close();
                } catch (IOException e) {
                    log.log(Level.WARNING, "An error occurred while closing index reader", e);
                }
            }
        }
    }

    /**
     * Get an indexReader for the Index database where a given file
     *
     * @param path the file to get the database for
     * @return The index database where the file should be located or null if
     *         it cannot be located.
     */
    public static IndexReader getIndexReader(String path) {
        IndexReader ret = null;

        RuntimeEnvironment env = RuntimeEnvironment.getInstance();
        File indexDir = new File(env.getDataRootFile(), "index");

        if (env.hasProjects()) {
            Project p = Project.getProject(path);
            if (p == null) {
                return null;
            }
            indexDir = new File(indexDir, p.getPath());
        }
        try {
            FSDirectory fsDirectory = FSDirectory.open(indexDir, NoLockFactory.getNoLockFactory());
            if (indexDir.exists() && IndexReader.indexExists(fsDirectory)) {
                ret = IndexReader.open(fsDirectory);
            }
        } catch (Exception ex) {
            log.log(Level.SEVERE, "Failed to open index: {0}", indexDir.getAbsolutePath());
            log.log(Level.FINE, "Stack Trace: ", ex);
        }
        return ret;
    }

    /**
     * Get the latest definitions for a file from the index.
     *
     * @param file the file whose definitions to find
     * @return definitions for the file, or {@code null} if they could not
     *         be found
     * @throws IOException            if an error happens when accessing the index
     * @throws ParseException         if an error happens when building the Lucene query
     * @throws ClassNotFoundException if the class for the stored definitions
     *                                instance cannot be found
     */
    public static Definitions getDefinitions(File file) throws IOException, ParseException, ClassNotFoundException {
        RuntimeEnvironment env = RuntimeEnvironment.getInstance();
        String path = env.getPathRelativeToSourceRoot(file, 0);

        IndexReader indexReader = getIndexReader(path);

        if (indexReader == null) {
            // No index, no definitions...
            return null;
        }

        try {
            Query q = new QueryBuilder().setPath(path).build();
            try (IndexSearcher searcher = new IndexSearcher(indexReader)) {
                TopDocs top = searcher.search(q, 1);
                if (top.totalHits == 0) {
                    // No hits, no definitions...
                    return null;
                }
                Document doc = searcher.doc(top.scoreDocs[0].doc);
                String foundPath = doc.get("path");

                // Only use the definitions if we found an exact match.
                if (path.equals(foundPath)) {
                    Fieldable tags = doc.getFieldable("tags");
                    if (tags != null) {
                        return Definitions.deserialize(tags.getBinaryValue());
                    }
                }
            }

        } finally {
            indexReader.close();
        }

        // Didn't find any definitions.
        return null;
    }

    @Override
    public boolean equals(Object obj) {
        if (obj == null) {
            return false;
        }
        if (getClass() != obj.getClass()) {
            return false;
        }
        final IndexDatabase other = (IndexDatabase) obj;
        return !(this.project != other.project && (this.project == null || !this.project.equals(other.project)));
    }

    @Override
    public int hashCode() {
        int hash = 7;
        hash = 41 * hash + (this.project == null ? 0 : this.project.hashCode());
        return hash;
    }

}

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
 * Copyright (c) 2006, 2010, Oracle and/or its affiliates. All rights reserved.
 * Portions Copyright (c) 2013 Takayuki Okazaki.
 */
package org.watermint.sourcecolon.org.opensolaris.opengrok.configuration;

import org.watermint.sourcecolon.org.opensolaris.opengrok.index.Filter;
import org.watermint.sourcecolon.org.opensolaris.opengrok.index.IgnoredNames;
import org.watermint.sourcecolon.org.opensolaris.opengrok.util.Executor;
import org.watermint.sourcecolon.org.opensolaris.opengrok.util.IOUtils;

import java.beans.XMLDecoder;
import java.beans.XMLEncoder;
import java.io.*;
import java.net.*;
import java.util.Date;
import java.util.List;
import java.util.Set;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * The RuntimeEnvironment class is used as a placeholder for the current
 * configuration this execution context (classloader) is using.
 */
public final class RuntimeEnvironment {
    public static final String DEFAULT_SOURCECOLON_ROOT;
    public static final String DEFAULT_SOURCECOLON_DATA;
    public static final String DEFAULT_SOURCECOLON_ETC;
    public static final String DEFAULT_SOURCECOLON_CONFIG;

    static {
        DEFAULT_SOURCECOLON_ROOT = System.getProperty("user.home") + File.separator + ".sourcecolon";
        DEFAULT_SOURCECOLON_ETC  = DEFAULT_SOURCECOLON_ROOT + File.separator + "etc";
        DEFAULT_SOURCECOLON_DATA = DEFAULT_SOURCECOLON_ROOT + File.separator + "data";
        DEFAULT_SOURCECOLON_CONFIG = DEFAULT_SOURCECOLON_ETC + File.separator + "config.xml";
    }

    private Configuration configuration;
    private final ThreadLocal<Configuration> threadConfig;

    private static final Logger log = Logger.getLogger(RuntimeEnvironment.class.getName());

    private static RuntimeEnvironment instance = new RuntimeEnvironment();

    /**
     * Get the one and only instance of the RuntimeEnvironment
     *
     * @return the one and only instance of the RuntimeEnvironment
     */
    public static RuntimeEnvironment getInstance() {
        return instance;
    }

    /**
     * Creates a new instance of RuntimeEnvironment. Private to ensure a
     * singleton pattern.
     */
    private RuntimeEnvironment() {
        configuration = new Configuration();
        threadConfig = new ThreadLocal<Configuration>() {
            @Override
            protected Configuration initialValue() {
                return configuration;
            }
        };
    }

    private String getCanonicalPath(String s) {
        try {
            File file = new File(s);
            if (!file.exists()) {
                return s;
            }
            return file.getCanonicalPath();
        } catch (IOException ex) {
            log.log(Level.SEVERE, "Failed to get canonical path", ex);
            return s;
        }
    }

    /**
     * Get the path to the where the index database is stored
     *
     * @return the path to the index database
     */
    public String getDataRootPath() {
        return threadConfig.get().getDataRoot();
    }

    /**
     * Get a file representing the index database
     *
     * @return the index database
     */
    public File getDataRootFile() {
        File ret = null;
        String file = getDataRootPath();
        if (file != null) {
            ret = new File(file);
        }

        return ret;
    }

    /**
     * Set the path to where the index database is stored
     *
     * @param dataRoot the index database
     */
    public void setDataRoot(String dataRoot) {
        threadConfig.get().setDataRoot(getCanonicalPath(dataRoot));
    }

    /**
     * Get the path to where the sources are located
     *
     * @return path to where the sources are located
     */
    public String getSourceRootPath() {
        return threadConfig.get().getSourceRoot();
    }

    /**
     * Get a file representing the directory where the sources are located
     *
     * @return A file representing the directory where the sources are located
     */
    public File getSourceRootFile() {
        File ret = null;
        String file = getSourceRootPath();
        if (file != null) {
            ret = new File(file);
        }

        return ret;
    }

    /**
     * Specify the source root
     *
     * @param sourceRoot the location of the sources
     */
    public void setSourceRoot(String sourceRoot) {
        threadConfig.get().setSourceRoot(getCanonicalPath(sourceRoot));
    }

    /**
     * Returns a path relative to source root. This would just be a simple
     * substring operation, except we need to support symlinks outside the
     * source root.
     *
     * @param file       A file to resolve
     * @param stripCount Number of characters past source root to strip
     * @return Path relative to source root
     * @throws IOException           If an IO error occurs
     * @throws FileNotFoundException If the file is not relative to source root
     */
    public String getPathRelativeToSourceRoot(File file, int stripCount) throws IOException {
        String canonicalPath = file.getCanonicalPath();
        String sourceRoot = getSourceRootPath();
        if (canonicalPath.startsWith(sourceRoot)) {
            return canonicalPath.substring(sourceRoot.length() + stripCount);
        }
        for (String allowedSymlink : getAllowedSymlinks()) {
            String allowedTarget = new File(allowedSymlink).getCanonicalPath();
            if (canonicalPath.startsWith(allowedTarget)) {
                return canonicalPath.substring(allowedTarget.length() + stripCount);
            }
        }
        throw new FileNotFoundException("Failed to resolve [" + canonicalPath + "] relative to source root [" + sourceRoot + "]");
    }

    /**
     * Do we have projects?
     *
     * @return true if we have projects
     */
    public boolean hasProjects() {
        List<Project> proj = getProjects();
        return (proj != null && !proj.isEmpty());
    }

    /**
     * Get all of the projects
     *
     * @return a list containing all of the projects (may be null)
     */
    public List<Project> getProjects() {
        return threadConfig.get().getProjects();
    }

    /**
     * Set the list of the projects
     *
     * @param projects the list of projects to use
     */
    public void setProjects(List<Project> projects) {
        threadConfig.get().setProjects(projects);
    }

    /**
     * Register this thread in the thread/configuration map (so that all
     * subsequent calls to the RuntimeEnvironment from this thread will use
     * the same configuration
     *
     * @return this instance
     */
    public RuntimeEnvironment register() {
        threadConfig.set(configuration);
        return this;
    }

    /**
     * Get the context name of the web application
     *
     * @return the web applications context name
     */
    public String getUrlPrefix() {
        return threadConfig.get().getUrlPrefix();
    }

    /**
     * Set the web context name
     *
     * @param urlPrefix the web applications context name
     */
    public void setUrlPrefix(String urlPrefix) {
        threadConfig.get().setUrlPrefix(urlPrefix);
    }

    /**
     * Get the name of the ctags program in use
     *
     * @return the name of the ctags program in use
     */
    public String getCtags() {
        return threadConfig.get().getCtags();
    }

    /**
     * Specify the CTags program to use
     *
     * @param ctags the ctags program to use
     */
    public void setCtags(String ctags) {
        threadConfig.get().setCtags(ctags);
    }

    public int getCachePages() {
        return threadConfig.get().getCachePages();
    }

    public void setCachePages(int cachePages) {
        threadConfig.get().setCachePages(cachePages);
    }

    public int getHitsPerPage() {
        return threadConfig.get().getHitsPerPage();
    }

    public void setHitsPerPage(int hitsPerPage) {
        threadConfig.get().setHitsPerPage(hitsPerPage);
    }

    private static Boolean exuberantCtagsAvailable = null;

    /**
     * Validate that I have a Exuberant ctags program I may use
     *
     * @return true if success, false otherwise
     */
    public boolean validateExuberantCtags() {
        if (exuberantCtagsAvailable != null) {
            return exuberantCtagsAvailable;
        }
        Executor executor = new Executor(new String[]{getCtags(), "--version"});
        executor.exec(false);
        String output = executor.getOutputString();

        exuberantCtagsAvailable = !(output == null || !output.contains("Exuberant Ctags"));

        return exuberantCtagsAvailable;
    }

    /**
     * Should we generate HTML or not during the indexing phase
     *
     * @return true if HTML should be generated during the indexing phase
     */
    public boolean isGenerateHtml() {
        return threadConfig.get().isGenerateHtml();
    }

    /**
     * Specify if we should generate HTML or not during the indexing phase
     *
     * @param generateHtml set this to true to pre-generate HTML
     */
    public void setGenerateHtml(boolean generateHtml) {
        threadConfig.get().setGenerateHtml(generateHtml);
    }

    /**
     * Set if we should compress the xref files or not
     *
     * @param compressXref set to true if the generated html files should be
     *                     compressed
     */
    public void setCompressXref(boolean compressXref) {
        threadConfig.get().setCompressXref(compressXref);
    }

    /**
     * Are we using compressed HTML files?
     *
     * @return {@code true} if the html-files should be compressed.
     */
    public boolean isCompressXref() {
        return threadConfig.get().isCompressXref();
    }

    public boolean isQuickContextScan() {
        return threadConfig.get().isQuickContextScan();
    }

    public void setQuickContextScan(boolean quickContextScan) {
        threadConfig.get().setQuickContextScan(quickContextScan);
    }

    /**
     * Set the project that is specified to be the default project to use. The
     * default project is the project you will search (from the web application)
     * if the page request didn't contain the cookie..
     *
     * @param defaultProject The default project to use
     */
    public void setDefaultProject(Project defaultProject) {
        threadConfig.get().setDefaultProject(defaultProject);
    }

    /**
     * Get the project that is specified to be the default project to use. The
     * default project is the project you will search (from the web application)
     * if the page request didn't contain the cookie..
     *
     * @return the default project (may be null if not specified)
     */
    public Project getDefaultProject() {
        return threadConfig.get().getDefaultProject();
    }

    /**
     * Chandan wrote the following answer on the opengrok-discuss list:
     * "Traditionally search engines (specially spiders) think that large files
     * are junk. Large files tend to be multimedia files etc., which text
     * search spiders do not want to chew. So they ignore the contents of
     * the file after a cutoff length. Lucene does this by number of words,
     * which is by default is 10,000."
     * By default OpenGrok will increase this limit to 60000, but it may be
     * overridden in the configuration file
     *
     * @return The maximum words to index
     */
    public int getIndexWordLimit() {
        return threadConfig.get().getIndexWordLimit();
    }

    /**
     * Set the number of words in a file Lucene will index.
     * See getIndexWordLimit for a better description.
     *
     * @param indexWordLimit the number of words to index in a single file
     */
    public void setIndexWordLimit(int indexWordLimit) {
        threadConfig.get().setIndexWordLimit(indexWordLimit);
    }

    /**
     * Is the verbosity flag turned on?
     *
     * @return true if we can print extra information
     */
    public boolean isVerbose() {
        return threadConfig.get().isVerbose();
    }

    /**
     * Set the verbosity flag (to add extra debug information in output)
     *
     * @param verbose new value
     */
    public void setVerbose(boolean verbose) {
        threadConfig.get().setVerbose(verbose);
    }

    /**
     * Is the progress print flag turned on?
     *
     * @return true if we can print per project progress %
     */
    public boolean isPrintProgress() {
        return threadConfig.get().isPrintProgress();
    }

    /**
     * Set the printing of progress % flag (user convenience)
     *
     * @param printP new value
     */
    public void setPrintProgress(boolean printP) {
        threadConfig.get().setPrintProgress(printP);
    }

    /**
     * Specify if a search may start with a wildcard. Note that queries
     * that start with a wildcard will give a significant impact on the
     * search performace.
     *
     * @param allowLeadingWildcard set to true to activate (disabled by default)
     */
    public void setAllowLeadingWildcard(boolean allowLeadingWildcard) {
        threadConfig.get().setAllowLeadingWildcard(allowLeadingWildcard);
    }

    /**
     * Is leading wildcards allowed?
     *
     * @return true if a search may start with a wildcard
     */
    public boolean isAllowLeadingWildcard() {
        return threadConfig.get().isAllowLeadingWildcard();
    }

    public IgnoredNames getIgnoredNames() {
        return threadConfig.get().getIgnoredNames();
    }

    public void setIgnoredNames(IgnoredNames ignoredNames) {
        threadConfig.get().setIgnoredNames(ignoredNames);
    }

    public Filter getIncludedNames() {
        return threadConfig.get().getIncludedNames();
    }

    public void setIncludedNames(Filter includedNames) {
        threadConfig.get().setIncludedNames(includedNames);
    }
    public boolean isUsingLuceneLocking() {
        return threadConfig.get().isUsingLuceneLocking();
    }

    public void setUsingLuceneLocking(boolean useLuceneLocking) {
        threadConfig.get().setUsingLuceneLocking(useLuceneLocking);
    }

    public boolean isIndexVersionedFilesOnly() {
        return threadConfig.get().isIndexVersionedFilesOnly();
    }

    public void setIndexVersionedFilesOnly(boolean indexVersionedFilesOnly) {
        threadConfig.get().setIndexVersionedFilesOnly(indexVersionedFilesOnly);
    }

    public Date getDateForLastIndexRun() {
        return threadConfig.get().getDateForLastIndexRun();
    }

    public Set<String> getAllowedSymlinks() {
        return threadConfig.get().getAllowedSymlinks();
    }

    public void setAllowedSymlinks(Set<String> allowedSymlinks) {
        threadConfig.get().setAllowedSymlinks(allowedSymlinks);
    }

    /**
     * Return whether e-mail addresses should be obfuscated in the xref.
     */
    public boolean isObfuscatingEMailAddresses() {
        return threadConfig.get().isObfuscatingEMailAddresses();
    }

    /**
     * Set whether e-mail addresses should be obfuscated in the xref.
     */
    public void setObfuscatingEMailAddresses(boolean obfuscate) {
        threadConfig.get().setObfuscatingEMailAddresses(obfuscate);
    }

    /**
     * Read an configuration file and set it as the current configuration.
     *
     * @param file the file to read
     * @throws IOException if an error occurs
     */
    public void readConfiguration(File file) throws IOException {
        setConfiguration(Configuration.read(file));
    }

    /**
     * Write the current configuration to a file
     *
     * @param file the file to write the configuration into
     * @throws IOException if an error occurs
     */
    public void writeConfiguration(File file) throws IOException {
        threadConfig.get().write(file);
    }

    /**
     * Write the current configuration to a socket
     *
     * @param host the host address to receive the configuration
     * @param port the port to use on the host
     * @throws IOException if an error occurs
     */
    public void writeConfiguration(InetAddress host, int port) throws IOException {
        Socket sock = new Socket(host, port);
        XMLEncoder e = new XMLEncoder(sock.getOutputStream());
        e.writeObject(threadConfig.get());
        e.close();
        IOUtils.close(sock);
    }

    protected void writeConfiguration() throws IOException {
        writeConfiguration(configServerSocket.getInetAddress(), configServerSocket.getLocalPort());
    }

    public void setConfiguration(Configuration configuration) {
        this.configuration = configuration;
        register();
    }

    public Configuration getConfiguration() {
        return this.threadConfig.get();
    }

    private ServerSocket configServerSocket;

    /**
     * Try to stop the configuration listener thread
     */
    public void stopConfigurationListenerThread() {
        IOUtils.close(configServerSocket);
    }

    /**
     * Start a thread to listen on a socket to receive new configurations
     * to use.
     *
     * @param endpoint The socket address to listen on
     * @return true if the endpoint was available (and the thread was started)
     */
    public boolean startConfigurationListenerThread(SocketAddress endpoint) {
        boolean ret = false;

        try {
            configServerSocket = new ServerSocket();
            configServerSocket.bind(endpoint);
            ret = true;
            final ServerSocket sock = configServerSocket;
            Thread t = new Thread(new Runnable() {
                @Override
                public void run() {
                    ByteArrayOutputStream bos = new ByteArrayOutputStream(1 << 13);
                    while (!sock.isClosed()) {
                        try (Socket s = sock.accept(); BufferedInputStream in = new BufferedInputStream(s.getInputStream())) {
                            bos.reset();
                            log.log(Level.FINE, "OpenGrok: Got request from {0}", s.getInetAddress().getHostAddress());
                            byte[] buf = new byte[1024];
                            int len;
                            while ((len = in.read(buf)) != -1) {
                                bos.write(buf, 0, len);
                            }
                            buf = bos.toByteArray();
                            if (log.isLoggable(Level.FINE)) {
                                log.log(Level.FINE, "new config:" + new String(buf));
                            }
                            XMLDecoder d = new XMLDecoder(new ByteArrayInputStream(buf));
                            Object obj = d.readObject();
                            d.close();

                            if (obj instanceof Configuration) {
                                setConfiguration((Configuration) obj);
                                log.log(Level.INFO, "Configuration updated: {0}", configuration.getSourceRoot());
                            }
                        } catch (IOException e) {
                            log.log(Level.SEVERE, "Error reading config file: ", e);
                        } catch (RuntimeException e) {
                            log.log(Level.SEVERE, "Error parsing config file: ", e);
                        }
                    }
                }
            });
            t.start();
        } catch (UnknownHostException ex) {
            log.log(Level.FINE, "Problem resolving sender: ", ex);
        } catch (IOException ex) {
            log.log(Level.FINE, "I/O error when waiting for config: ", ex);
        }

        if (!ret && configServerSocket != null) {
            IOUtils.close(configServerSocket);
        }

        return ret;
    }
}

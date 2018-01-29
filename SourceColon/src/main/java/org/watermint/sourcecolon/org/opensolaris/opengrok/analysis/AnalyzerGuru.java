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
 * Copyright (c) 2005, 2011, Oracle and/or its affiliates. All rights reserved.
 * Portions Copyright (c) 2013 Takayuki Okazaki.
 */
package org.watermint.sourcecolon.org.opensolaris.opengrok.analysis;

import org.apache.lucene.document.DateTools;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.FileAnalyzer.Genre;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.archive.BZip2AnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.archive.GZIPAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.archive.TarAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.archive.ZipAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.c.CAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.c.CxxAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.csharp.CSharpAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.data.IgnorantAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.data.ImageAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.document.TroffAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.executables.ELFAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.executables.JarAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.executables.JavaClassAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.fortran.FortranAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.java.JavaAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.javascript.JavaScriptAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.lisp.LispAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.perl.PerlAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.php.PhpAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.plain.PlainAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.plain.XMLAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.python.PythonAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.sh.ShAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.sql.SQLAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.tcl.TclAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.vb.VBAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.configuration.Project;
import org.watermint.sourcecolon.org.opensolaris.opengrok.web.Util;

import java.io.*;
import java.util.*;

/**
 * Manages and provides Analyzers as needed. Please see
 * <a href="https://github.com/OpenGrok/OpenGrok/wiki/OpenGrok-Internals">
 * this</a> page for a great description of the purpose of the AnalyzerGuru.
 * <p/>
 * Created on September 22, 2005
 *
 * @author Chandan
 */
public class AnalyzerGuru {

    /**
     * The default {@code FileAnalyzerFactory} instance.
     */
    private static final FileAnalyzerFactory
            DEFAULT_ANALYZER_FACTORY = new FileAnalyzerFactory();

    /**
     * Map from file names to analyzer factories.
     */
    private static final Map<String, FileAnalyzerFactory>
            FILE_NAMES = new HashMap<>();

    /**
     * Map from file extensions to analyzer factories.
     */
    private static final Map<String, FileAnalyzerFactory>
            ext = new HashMap<>();

    // @TODO: have a comparator
    /**
     * Map from magic strings to analyzer factories.
     */
    private static final SortedMap<String, FileAnalyzerFactory>
            magics = new TreeMap<>();

    /**
     * List of matcher objects which can be used to determine which analyzer
     * factory to use.
     */
    private static final List<FileAnalyzerFactory.Matcher>
            matchers = new ArrayList<>();

    /**
     * List of all registered {@code FileAnalyzerFactory} instances.
     */
    private static final List<FileAnalyzerFactory>
            factories = new ArrayList<>();

    /*
     * If you write your own analyzer please register it here
     */
    static {
        FileAnalyzerFactory[] analyzers = {
                DEFAULT_ANALYZER_FACTORY,
                new IgnorantAnalyzerFactory(),
                new BZip2AnalyzerFactory(),
                new XMLAnalyzerFactory(),
                new TroffAnalyzerFactory(),
                new ELFAnalyzerFactory(),
                new JavaClassAnalyzerFactory(),
                new ImageAnalyzerFactory(),
                JarAnalyzerFactory.DEFAULT_INSTANCE,
                ZipAnalyzerFactory.DEFAULT_INSTANCE,
                new TarAnalyzerFactory(),
                new CAnalyzerFactory(),
                new CSharpAnalyzerFactory(),
                new VBAnalyzerFactory(),
                new CxxAnalyzerFactory(),
                new ShAnalyzerFactory(),
                PlainAnalyzerFactory.DEFAULT_INSTANCE,
                new GZIPAnalyzerFactory(),
                new JavaAnalyzerFactory(),
                new JavaScriptAnalyzerFactory(),
                new PythonAnalyzerFactory(),
                new PerlAnalyzerFactory(),
                new PhpAnalyzerFactory(),
                new LispAnalyzerFactory(),
                new TclAnalyzerFactory(),
                new SQLAnalyzerFactory(),
                new FortranAnalyzerFactory()
        };

        for (FileAnalyzerFactory analyzer : analyzers) {
            registerAnalyzer(analyzer);
        }
    }

    /**
     * Register a {@code FileAnalyzerFactory} instance.
     */
    private static void registerAnalyzer(FileAnalyzerFactory factory) {
        for (String name : factory.getFileNames()) {
            FileAnalyzerFactory old = FILE_NAMES.put(name, factory);
            assert old == null :
                    "name '" + name + "' used in multiple analyzers";
        }
        for (String suffix : factory.getSuffixes()) {
            FileAnalyzerFactory old = ext.put(suffix, factory);
            assert old == null :
                    "suffix '" + suffix + "' used in multiple analyzers";
        }
        for (String magic : factory.getMagicStrings()) {
            FileAnalyzerFactory old = magics.put(magic, factory);
            assert old == null :
                    "magic '" + magic + "' used in multiple analyzers";
        }
        matchers.addAll(factory.getMatchers());
        factories.add(factory);
    }

    /**
     * Instruct the AnalyzerGuru to use a given analyzer for a given
     * file extension.
     *
     * @param extension the file-extension to add
     * @param factory   a factory which creates
     *                  the analyzer to use for the given extension
     *                  (if you pass null as the analyzer, you will disable
     *                  the analyzer used for that extension)
     */
    public static void addExtension(String extension,
                                    FileAnalyzerFactory factory) {
        if (factory == null) {
            ext.remove(extension);
        } else {
            ext.put(extension, factory);
        }
    }

    /**
     * Get the default Analyzer.
     */
    public static FileAnalyzer getAnalyzer() {
        return DEFAULT_ANALYZER_FACTORY.getAnalyzer();
    }

    /**
     * Get an analyzer suited to analyze a file. This function will reuse
     * analyzers since they are costly.
     *
     * @param in   Input stream containing data to be analyzed
     * @param file Name of the file to be analyzed
     * @return An analyzer suited for that file content
     * @throws java.io.IOException If an error occurs while accessing the
     *                             data in the input stream.
     */
    public static FileAnalyzer getAnalyzer(InputStream in, String file) throws IOException {
        FileAnalyzerFactory factory = find(in, file);
        if (factory == null) {
            return getAnalyzer();
        }
        return factory.getAnalyzer();
    }

    /**
     * Create a Lucene document and fill in the required fields
     *
     * @param file The file to index
     * @param in   The data to generate the index for
     * @param path Where the file is located (from source root)
     * @return The Lucene document to add to the index database
     * @throws java.io.IOException If an exception occurs while collecting the data
     */
    public Document getDocument(File file, InputStream in, String path,
                                FileAnalyzer fa) throws IOException {
        Document doc = new Document();
        String date = DateTools.timeToString(file.lastModified(),
                DateTools.Resolution.MILLISECOND);
        doc.add(new Field("u", Util.path2uid(path, date),
                Field.Store.YES, Field.Index.NOT_ANALYZED));
        doc.add(new Field("fullpath", file.getAbsolutePath(),
                Field.Store.NO, Field.Index.NOT_ANALYZED));

        doc.add(new Field("date", date, Field.Store.YES, Field.Index.NOT_ANALYZED));
        if (path != null) {
            doc.add(new Field("path", path, Field.Store.YES, Field.Index.ANALYZED));
            Project project = Project.getProject(path);
            if (project != null) {
                doc.add(new Field("project", project.getPath(), Field.Store.YES, Field.Index.ANALYZED));
            }
        }

        if (fa != null) {
            Genre g = fa.getGenre();
            if (g == Genre.PLAIN || g == Genre.XREFABLE || g == Genre.HTML) {
                doc.add(new Field("t", g.typeName(), Field.Store.YES,
                        Field.Index.NOT_ANALYZED));
            }
            fa.analyze(doc, in);
        }

        return doc;
    }

    /**
     * Write a browsable version of the file
     *
     *
     * @param factory    The analyzer factory for this filetype
     * @param in         The input stream containing the data
     * @param out        Where to write the result
     * @param defs       definitions for the source file, if available
     * @param project    Project the file belongs to
     * @throws java.io.IOException If an error occurs while creating the
     *                             output
     */
    public static void writeXref(FileAnalyzerFactory factory, Reader in, Writer out, Definitions defs, Project project)
            throws IOException {
        Reader input = in;
        if (factory.getGenre() == Genre.PLAIN) {
            // This is some kind of text file, so we need to expand tabs to
            // spaces to match the project's tab settings.
            input = ExpandTabsReader.wrap(in, project);
        }
        factory.writeXref(input, out, defs, project);
    }

    /**
     * Get the genre for a named class (this is most likely an analyzer)
     *
     * @param factory the analyzer factory to get the genre for
     * @return The genre of this class (null if not found)
     */
    public static Genre getGenre(FileAnalyzerFactory factory) {
        if (factory != null) {
            return factory.getGenre();
        }
        return null;
    }

    /**
     * Find a {@code FileAnalyzerFactory} with the specified class name. If one
     * doesn't exist, create one and register it.
     *
     * @param factoryClassName name of the factory class
     * @return a file analyzer factory
     * @throws ClassNotFoundException if there is no class with that name
     * @throws ClassCastException     if the class is not a subclass of {@code
     *                                FileAnalyzerFactory}
     * @throws IllegalAccessException if the constructor cannot be accessed
     * @throws InstantiationException if the class cannot be instantiated
     */
    public static FileAnalyzerFactory findFactory(String factoryClassName)
            throws ClassNotFoundException, IllegalAccessException,
            InstantiationException {
        return findFactory(Class.forName(factoryClassName));
    }

    /**
     * Find a {@code FileAnalyzerFactory} which is an instance of the specified
     * class. If one doesn't exist, create one and register it.
     *
     * @param factoryClass the factory class
     * @return a file analyzer factory
     * @throws ClassCastException     if the class is not a subclass of {@code
     *                                FileAnalyzerFactory}
     * @throws IllegalAccessException if the constructor cannot be accessed
     * @throws InstantiationException if the class cannot be instantiated
     */
    private static FileAnalyzerFactory findFactory(Class<?> factoryClass)
            throws InstantiationException, IllegalAccessException {
        for (FileAnalyzerFactory f : factories) {
            if (f.getClass() == factoryClass) {
                return f;
            }
        }
        FileAnalyzerFactory f =
                (FileAnalyzerFactory) factoryClass.newInstance();
        registerAnalyzer(f);
        return f;
    }

    /**
     * Finds a suitable analyser class for file name. If the analyzer cannot
     * be determined by the file extension, try to look at the data in the
     * InputStream to find a suitable analyzer.
     * <p/>
     * Use if you just want to find file type.
     *
     * @param in   The input stream containing the data
     * @param file The file name to get the analyzer for
     * @return the analyzer factory to use
     * @throws java.io.IOException If a problem occurs while reading the data
     */
    public static FileAnalyzerFactory find(InputStream in, String file)
            throws IOException {
        FileAnalyzerFactory factory = find(file);
        //TODO above is not that great, since if 2 analyzers share one extension
        //then only the first one registered will own it
        //it would be cool if above could return more analyzers and below would
        //then decide between them ...
        if (factory != null) {
            return factory;
        }
        return find(in);
    }

    /**
     * Finds a suitable analyser class for file name.
     *
     * @param file The file name to get the analyzer for
     * @return the analyzer factory to use
     */
    public static FileAnalyzerFactory find(String file) {
        String path = file;
        int i = 0;
        if (((i = path.lastIndexOf('/')) > 0 || (i = path.lastIndexOf('\\')) > 0)
                && (i + 1 < path.length())) {
            path = path.substring(i + 1);
        }
        int dotPos = path.lastIndexOf('.');
        if (dotPos >= 0) {
            FileAnalyzerFactory factory =
                    ext.get(path.substring(dotPos + 1).toUpperCase(Locale.getDefault()));
            if (factory != null) {
                return factory;
            }
        }
        // file doesn't have any of the extensions we know, try full match
        return FILE_NAMES.get(path.toUpperCase(Locale.getDefault()));
    }

    /**
     * Finds a suitable analyser class for the data in this stream
     *
     * @param in The stream containing the data to analyze
     * @return the analyzer factory to use
     * @throws java.io.IOException if an error occurs while reading data from
     *                             the stream
     */
    public static FileAnalyzerFactory find(InputStream in) throws IOException {
        in.mark(8);
        byte[] content = new byte[8];
        int len = in.read(content);
        in.reset();
        if (len < 4) {
            return null;
        }

        FileAnalyzerFactory factory = find(content);
        if (factory != null) {
            return factory;
        }

        for (FileAnalyzerFactory.Matcher matcher : matchers) {
            FileAnalyzerFactory fac = matcher.isMagic(content, in);
            if (fac != null) {
                return fac;
            }
        }

        return null;
    }

    /**
     * Finds a suitable analyser class for a magic signature
     *
     * @param signature the magic signature look up
     * @return the analyzer factory to use
     */
    private static FileAnalyzerFactory find(byte[] signature)
            throws IOException {
        // XXX this assumes ISO-8859-1 encoding (and should work in most cases
        // for US-ASCII, UTF-8 and other ISO-8859-* encodings, but not always),
        // we should try to be smarter than this...
        char[] chars = new char[signature.length > 8 ? 8 : signature.length];
        for (int i = 0; i < chars.length; i++) {
            chars[i] = (char) (0xFF & signature[i]);
        }

        String sig = new String(chars);

        FileAnalyzerFactory a = magics.get(sig);
        if (a == null) {
            String sigWithoutBOM = stripBOM(signature);
            for (Map.Entry<String, FileAnalyzerFactory> entry :
                    magics.entrySet()) {
                if (sig.startsWith(entry.getKey())) {
                    return entry.getValue();
                }
                // See if text files have the magic sequence if we remove the
                // byte-order marker
                if (sigWithoutBOM != null &&
                        entry.getValue().getGenre() == Genre.PLAIN &&
                        sigWithoutBOM.startsWith(entry.getKey())) {
                    return entry.getValue();
                }
            }
        }
        return a;
    }

    /**
     * Byte-order markers.
     */
    private static final Map<String, byte[]> BOMS =
            new HashMap<>();

    static {
        BOMS.put("UTF-8", new byte[]{(byte) 0xEF, (byte) 0xBB, (byte) 0xBF});
        BOMS.put("UTF-16BE", new byte[]{(byte) 0xFE, (byte) 0xFF});
        BOMS.put("UTF-16LE", new byte[]{(byte) 0xFF, (byte) 0xFE});
    }

    /**
     * Strip away the byte-order marker from the string, if it has one.
     *
     * @param sig a sequence of bytes from which to remove the BOM
     * @return a string without the byte-order marker, or <code>null</code> if
     *         the string doesn't start with a BOM
     */
    public static String stripBOM(byte[] sig) throws IOException {
        for (Map.Entry<String, byte[]> entry : BOMS.entrySet()) {
            String encoding = entry.getKey();
            byte[] bom = entry.getValue();
            if (sig.length > bom.length) {
                int i = 0;
                while (i < bom.length && sig[i] == bom[i]) {
                    i++;
                }
                if (i == bom.length) {
                    // BOM matched beginning of signature
                    return new String(
                            sig,
                            bom.length,                // offset
                            sig.length - bom.length,   // length
                            encoding);
                }
            }
        }
        return null;
    }
}

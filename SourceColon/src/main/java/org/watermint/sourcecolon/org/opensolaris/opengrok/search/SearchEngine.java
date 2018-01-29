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
 * Copyright 2010 Sun Micosystems.  All rights reserved.
 * Use is subject to license terms.
 * Portions Copyright (c) 2013 Takayuki Okazaki.
 */

package org.watermint.sourcecolon.org.opensolaris.opengrok.search;

import org.apache.lucene.document.Document;
import org.apache.lucene.document.Fieldable;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.MultiReader;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopScoreDocCollector;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.Version;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.CompatibleAnalyser;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.Definitions;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.FileAnalyzer.Genre;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.TagFilter;
import org.watermint.sourcecolon.org.opensolaris.opengrok.configuration.Project;
import org.watermint.sourcecolon.org.opensolaris.opengrok.configuration.RuntimeEnvironment;
import org.watermint.sourcecolon.org.opensolaris.opengrok.search.Summary.Fragment;
import org.watermint.sourcecolon.org.opensolaris.opengrok.search.context.Context;
import org.watermint.sourcecolon.org.opensolaris.opengrok.util.IOUtils;

import java.io.*;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.zip.GZIPInputStream;

/**
 * This is an encapsulation of the details on how to seach in the index
 * database.
 *
 * @author Trond Norbye 2005
 * @author Lubos Kosco 2010 - upgrade to lucene 3.0.0
 */
public class SearchEngine {
    /**
     * Message text used when logging exceptions thrown when searching.
     */
    private static final String SEARCH_EXCEPTION_MSG = "Exception searching";

    //NOTE below will need to be changed after new lucene upgrade, if they
    //increase the version - every change of below makes us incompatible with the
    //old index and we need to ask for reindex
    /**
     * version of lucene index common for whole app
     */
    public static final Version LUCENE_VERSION = Version.LUCENE_36;

    /**
     * Holds value of property definition.
     */
    private String definition;

    /**
     * Holds value of property file.
     */
    private String file;

    /**
     * Holds value of property freetext.
     */
    private String freetext;

    /**
     * Holds value of property history.
     */
    private String history;

    /**
     * Holds value of property symbol.
     */
    private String symbol;

    /**
     * Holds value of property indexDatabase.
     */
    private Query query;
    private final CompatibleAnalyser analyzer = new CompatibleAnalyser();
    private Context sourceContext;
    private Summarizer summarizer;
    // internal structure to hold the results from lucene
    private final List<org.apache.lucene.document.Document> docs;
    private final char[] content = new char[1024 * 8];
    private String source;
    private String data;
    private static final boolean docsScoredInOrder = false;

    private int hitsPerPage = RuntimeEnvironment.getInstance().getHitsPerPage();
    private int cachePages = RuntimeEnvironment.getInstance().getCachePages();
    int totalHits = 0;
    private static final Logger log = Logger.getLogger(SearchEngine.class.getName());

    private ScoreDoc[] hits;
    private TopScoreDocCollector collector;
    private IndexSearcher searcher;
    private boolean allCollected;

    /**
     * Creates a new instance of SearchEngine
     */
    public SearchEngine() {
        docs = new ArrayList<>();
    }

    /**
     * Create a QueryBuilder using the fields that have been set on this
     * SearchEngine.
     *
     * @return a query builder
     */
    private QueryBuilder createQueryBuilder() {
        return new QueryBuilder()
                .setFreetext(freetext)
                .setDefs(definition)
                .setRefs(symbol)
                .setPath(file);
    }

    public boolean isValidQuery() {
        boolean ret;
        try {
            query = createQueryBuilder().build();
            ret = (query != null);
        } catch (Exception e) {
            ret = false;
        }

        return ret;
    }

    /**
     * @param paging whether to use paging (if yes, first X pages will load faster)
     * @param root   which db to search
     * @throws IOException
     */
    private void searchSingleDatabase(File root, boolean paging) throws IOException {
        IndexReader ireader = IndexReader.open(FSDirectory.open(root));
        searcher = new IndexSearcher(ireader);
        collector = TopScoreDocCollector.create(hitsPerPage * cachePages, docsScoredInOrder);
        searcher.search(query, collector);
        totalHits = collector.getTotalHits();
        if (!paging) {
            collector = TopScoreDocCollector.create(totalHits, docsScoredInOrder);
            searcher.search(query, collector);
        }
        hits = collector.topDocs().scoreDocs;
        for (ScoreDoc hit : hits) {
            int docId = hit.doc;
            Document d = searcher.doc(docId);
            docs.add(d);
        }
    }

    /**
     * @param paging whether to use paging (if yes, first X pages will load faster)
     * @param root   list of projects to search
     * @throws IOException
     */
    private void searchMultiDatabase(List<Project> root, boolean paging) throws IOException {
        IndexReader[] searchables = new IndexReader[root.size()];
        File droot = new File(RuntimeEnvironment.getInstance().getDataRootFile(), "index");
        int ii = 0;
        for (Project project : root) {
            searchables[ii++] = (IndexReader.open(FSDirectory.open(new File(droot, project.getPath()))));
        }
        searcher = new IndexSearcher(new MultiReader(searchables));
        collector = TopScoreDocCollector.create(hitsPerPage * cachePages, docsScoredInOrder);
        searcher.search(query, collector);
        totalHits = collector.getTotalHits();
        if (!paging) {
            collector = TopScoreDocCollector.create(totalHits, docsScoredInOrder);
            searcher.search(query, collector);
        }
        hits = collector.topDocs().scoreDocs;
        for (ScoreDoc hit : hits) {
            int docId = hit.doc;
            Document d = searcher.doc(docId);
            docs.add(d);
        }
    }

    public String getQuery() {
        return query.toString();
    }

    /**
     * Execute a search. Before calling this function, you must set the
     * appropriate seach critera with the set-functions.
     * Note that this search will return the first cachePages of hitsPerPage, for more you need to call more
     *
     * @return The number of hits
     */
    public int search() {
        source = RuntimeEnvironment.getInstance().getSourceRootPath();
        data = RuntimeEnvironment.getInstance().getDataRootPath();
        docs.clear();

        QueryBuilder queryBuilder = createQueryBuilder();

        try {
            query = queryBuilder.build();
            if (query != null) {
                RuntimeEnvironment env = RuntimeEnvironment.getInstance();
                File root = new File(env.getDataRootFile(), "index");
                System.out.println(root.getPath());
                if (env.hasProjects()) {
                    // search all projects
                    //TODO support paging per project (in search.java)
                    //TODO optimize if only one project by falling back to SingleDatabase ?
                    searchMultiDatabase(env.getProjects(), false);
                } else {
                    // search the index database
                    searchSingleDatabase(root, true);
                }
            }
        } catch (Exception e) {
            log.log(Level.WARNING, SEARCH_EXCEPTION_MSG, e);
        }

        if (!docs.isEmpty()) {
            sourceContext = null;
            summarizer = null;
            try {
                sourceContext = new Context(query, queryBuilder.getQueries());
                if (sourceContext.isEmpty()) {
                    sourceContext = null;
                }
                summarizer = new Summarizer(query, analyzer);
            } catch (Exception e) {
                log.log(Level.WARNING, "An error occured while creating summary", e);
            }
        }
        return hits.length;
    }

    /**
     * get results , if no search was started before, no results are returned
     * this method will requery if end end is more than first query from search,
     * hence performance hit applies, if you want results in later pages than number of cachePages
     * also end has to be bigger than start !
     *
     * @param start start of the hit list
     * @param end   end of the hit list
     * @param ret   list of results from start to end or null/empty if no search was started
     */
    public void results(int start, int end, List<Hit> ret) {

        //return if no start search() was done
        if (hits == null || (end < start)) {
            ret.clear();
            return;
        }

        ret.clear();

        //TODO check if below fits for if end=old hits.length, or it should include it
        if (end > hits.length & !allCollected) {
            //do the requery, we want more than 5 pages
            collector = TopScoreDocCollector.create(totalHits, docsScoredInOrder);
            try {
                searcher.search(query, collector);
            } catch (Exception e) { // this exception should never be hit, since search() will hit this before
                log.log(Level.WARNING, SEARCH_EXCEPTION_MSG, e);
            }
            hits = collector.topDocs().scoreDocs;
            Document d = null;
            for (int i = start; i < hits.length; i++) {
                int docId = hits[i].doc;
                try {
                    d = searcher.doc(docId);
                } catch (Exception e) {
                    log.log(Level.SEVERE, SEARCH_EXCEPTION_MSG, e);
                }
                docs.add(d);
            }
            allCollected = true;
        }

        //TODO generation of ret(results) could be cashed and consumers of engine would just print them in whatever form they need, this way we could get rid of docs
        // the only problem is that count of docs is usually smaller than number of results
        for (int ii = start; ii < end; ++ii) {
            boolean alt = (ii % 2 == 0);
            boolean hasContext = false;
            try {
                Document doc = docs.get(ii);
                String filename = doc.get("path");

                Genre genre = Genre.get(doc.get("t"));
                Definitions tags = null;
                Fieldable tagsField = doc.getFieldable("tags");
                if (tagsField != null) {
                    tags = Definitions.deserialize(tagsField.getBinaryValue());
                }
                int nhits = docs.size();

                if (sourceContext != null) {
                    try {
                        if (Genre.PLAIN == genre && (source != null)) {
                            hasContext = sourceContext.getContext(IOUtils.readerWithCharsetDetect(source +
                                    filename), null, null, null, filename,
                                    tags, nhits > 100, ret);
                        } else if (Genre.XREFABLE == genre && data != null && summarizer != null) {
                            int l = 0;
                            Reader r = null;
                            if (RuntimeEnvironment.getInstance().isCompressXref()) {
                                r = new TagFilter(new BufferedReader(new InputStreamReader(new GZIPInputStream(new FileInputStream(data + "/xref" + filename + ".gz")))));
                            } else {
                                r = new TagFilter(new BufferedReader(new FileReader(data + "/xref" + filename)));
                            }
                            try {
                                l = r.read(content);
                            } finally {
                                IOUtils.close(r);
                            }
                            //TODO FIX below fragmenter according to either summarizer or context (to get line numbers, might be hard, since xref writers will need to be fixed too, they generate just one line of html code now :( )
                            Summary sum = summarizer.getSummary(new String(content, 0, l));
                            Fragment fragments[] = sum.getFragments();
                            for (Fragment fragment : fragments) {
                                String match = fragment.toString();
                                if (match.length() > 0) {
                                    if (!fragment.isEllipsis()) {
                                        Hit hit = new Hit(filename, fragment.toString(), "", true, alt);
                                        ret.add(hit);
                                    }
                                    hasContext = true;
                                }
                            }
                        } else {
                            log.warning("Unknown genre: " + genre + " for " + filename);
                            hasContext |= sourceContext.getContext(null, null, null, null, filename, tags, false, ret);
                        }
                    } catch (FileNotFoundException exp) {
                        log.warning("Couldn't read summary from " + filename + " (" + exp.getMessage() + ")");
                        hasContext |= sourceContext.getContext(null, null, null, null, filename, tags, false, ret);
                    }
                }
                if (!hasContext) {
                    ret.add(new Hit(filename, "...", "", false, alt));
                }
            } catch (IOException | ClassNotFoundException e) {
                log.log(Level.WARNING, SEARCH_EXCEPTION_MSG, e);
            }
        }

    }

    /**
     * Getter for property definition.
     *
     * @return Value of property definition.
     */
    public String getDefinition() {
        return this.definition;
    }

    /**
     * Setter for property definition.
     *
     * @param definition New value of property definition.
     */
    public void setDefinition(String definition) {
        this.definition = definition;
    }

    /**
     * Getter for property file.
     *
     * @return Value of property file.
     */
    public String getFile() {
        return this.file;
    }

    /**
     * Setter for property file.
     *
     * @param file New value of property file.
     */
    public void setFile(String file) {
        this.file = file;
    }

    /**
     * Getter for property freetext.
     *
     * @return Value of property freetext.
     */
    public String getFreetext() {
        return this.freetext;
    }

    /**
     * Setter for property freetext.
     *
     * @param freetext New value of property freetext.
     */
    public void setFreetext(String freetext) {
        this.freetext = freetext;
    }

    /**
     * Getter for property history.
     *
     * @return Value of property history.
     */
    public String getHistory() {
        return this.history;
    }

    /**
     * Setter for property history.
     *
     * @param history New value of property history.
     */
    public void setHistory(String history) {
        this.history = history;
    }

    /**
     * Getter for property symbol.
     *
     * @return Value of property symbol.
     */
    public String getSymbol() {
        return this.symbol;
    }

    /**
     * Setter for property symbol.
     *
     * @param symbol New value of property symbol.
     */
    public void setSymbol(String symbol) {
        this.symbol = symbol;
    }
}

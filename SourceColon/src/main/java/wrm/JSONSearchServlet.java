package wrm;

import java.io.IOException;
import java.net.URLDecoder;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.tools.ant.util.Base64Converter;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.watermint.sourcecolon.org.opensolaris.opengrok.configuration.Project;
import org.watermint.sourcecolon.org.opensolaris.opengrok.configuration.RuntimeEnvironment;
import org.watermint.sourcecolon.org.opensolaris.opengrok.search.Hit;
import org.watermint.sourcecolon.org.opensolaris.opengrok.search.SearchEngine;

public class JSONSearchServlet extends HttpServlet {

    private static final long serialVersionUID = -1675062445999680962L;
    private static final Base64Converter conv = new Base64Converter();
    private static final int MAX_RESULTS = 1000;
    private static final String PARAM_FREETEXT = "freetext";
    private static final String PARAM_DEF = "defs";
    private static final String PARAM_SYMBOL = "refs";
    private static final String PARAM_PATH = "path";
    private static final String PARAM_HIST = "hist";
    private static final String PARAM_MAXRESULTS = "maxresults";
    private static final String ATTRIBUTE_DIRECTORY = "directory";
    private static final String ATTRIBUTE_FILENAME = "filename";
    private static final String ATTRIBUTE_LINENO = "lineno";
    private static final String ATTRIBUTE_LINE = "line";
    private static final String ATTRIBUTE_PATH = "path";
    private static final String ATTRIBUTE_RESULTS = "results";
    private static final String ATTRIBUTE_DURATION = "duration";
    private static final String ATTRIBUTE_RESULT_COUNT = "resultcount";

//  http://localhost:8080/mysearch?symbol=Date&maxresults=80
    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        JSONObject result = new JSONObject();
        SearchEngine engine = new SearchEngine();

        boolean valid = false;

        String freetext = req.getParameter(PARAM_FREETEXT);
        String def = req.getParameter(PARAM_DEF);
        String symbol = req.getParameter(PARAM_SYMBOL);
        String path = req.getParameter(PARAM_PATH);
        String hist = req.getParameter(PARAM_HIST);

        if (freetext != null) {
            freetext = URLDecoder.decode(freetext);
            engine.setFreetext(freetext);
            valid = true;
            result.put(PARAM_FREETEXT, freetext);
        }

        if (def != null) {
            def = URLDecoder.decode(def);
            engine.setDefinition(def);
            valid = true;
            result.put(PARAM_DEF, def);
        }

        if (symbol != null) {
            symbol = URLDecoder.decode(symbol);
            engine.setSymbol(symbol);
            valid = true;
            result.put(PARAM_SYMBOL, symbol);
        }

        if (path != null) {
            path = URLDecoder.decode(path);
            engine.setFile(path);
            valid = true;
            result.put(PARAM_PATH, path);
        }

        if (hist != null) {
            hist = URLDecoder.decode(hist);
            engine.setHistory(hist);
            valid = true;
            result.put(PARAM_HIST, hist);
        }

        if (valid) {
            long start = System.currentTimeMillis();
            //保留现场
            RuntimeEnvironment env = RuntimeEnvironment.getInstance();
            List<Project> projects = env.getProjects();

            List<Project> myprojects = new ArrayList<Project>();
            env.setProjects(myprojects);
            int numResults = engine.search();
            env.setProjects(projects);

            int maxResults = MAX_RESULTS;
            String maxResultsParam = req.getParameter(PARAM_MAXRESULTS);
            if (maxResultsParam != null) {
                try {
                    maxResults = Integer.parseInt(maxResultsParam);
                    result.put(PARAM_MAXRESULTS, maxResults);
                } catch (NumberFormatException ex) {
                }
            }
            List<Hit> results = new ArrayList<>(maxResults);
            engine.results(0,
                    numResults > maxResults ? maxResults : numResults, results);
            JSONArray resultsArray = new JSONArray();

//            HashSet directorySet=new HashSet<String>();
//            for (Hit hit : results) {
//                if(!directorySet.contains(hit.getPath())){
//                    directorySet.add(hit.getPath());
//                    JSONObject hitJson = new JSONObject();
//                    hitJson.put(ATTRIBUTE_DIRECTORY,
//                            JSONObject.escape(hit.getDirectory()));
//                    hitJson.put(ATTRIBUTE_FILENAME,
//                            JSONObject.escape(hit.getFilename()));
//                    hitJson.put(ATTRIBUTE_PATH, hit.getPath());
//                    resultsArray.add(hitJson);
//                }
//            }
//            result.put(ATTRIBUTE_RESULT_COUNT, resultsArray.size());
//            result.put(ATTRIBUTE_RESULTS, resultsArray);

            for (Hit hit : results) {
                JSONObject hitJson = new JSONObject();
                hitJson.put(ATTRIBUTE_DIRECTORY,
                        JSONObject.escape(hit.getDirectory()));
                hitJson.put(ATTRIBUTE_FILENAME,
                        JSONObject.escape(hit.getFilename()));
                hitJson.put(ATTRIBUTE_LINENO, hit.getLineno());
                hitJson.put(ATTRIBUTE_LINE, conv.encode(hit.getLine()));
                hitJson.put(ATTRIBUTE_PATH, hit.getPath());
                resultsArray.add(hitJson);

            }

            long duration = System.currentTimeMillis() - start;

            result.put(ATTRIBUTE_DURATION, duration);
            result.put(ATTRIBUTE_RESULT_COUNT, results.size());
            result.put(ATTRIBUTE_RESULTS, resultsArray);


            System.out.println(result);
        }
        resp.getWriter().write(result.toString());
    }

/*    protected void before(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        JSONObject result = new JSONObject();
        SearchEngine engine = new SearchEngine();

        boolean valid = false;

        String freetext = req.getParameter(PARAM_FREETEXT);
        String def = req.getParameter(PARAM_DEF);
        String symbol = req.getParameter(PARAM_SYMBOL);
        String path = req.getParameter(PARAM_PATH);
        String hist = req.getParameter(PARAM_HIST);

        if (freetext != null) {
            freetext = URLDecoder.decode(freetext);
            engine.setFreetext(freetext);
            valid = true;
            result.put(PARAM_FREETEXT, freetext);
        }

        if (def != null) {
            def = URLDecoder.decode(def);
            engine.setDefinition(def);
            valid = true;
            result.put(PARAM_DEF, def);
        }

        if (symbol != null) {
            symbol = URLDecoder.decode(symbol);
            engine.setSymbol(symbol);
            valid = true;
            result.put(PARAM_SYMBOL, symbol);
        }

        if (path != null) {
            path = URLDecoder.decode(path);
            engine.setFile(path);
            valid = true;
            result.put(PARAM_PATH, path);
        }

        if (hist != null) {
            hist = URLDecoder.decode(hist);
            engine.setHistory(hist);
            valid = true;
            result.put(PARAM_HIST, hist);
        }

        if (valid) {
            long start = System.currentTimeMillis();

            int numResults = engine.search();
            int maxResults = MAX_RESULTS;
            String maxResultsParam = req.getParameter(PARAM_MAXRESULTS);
            if (maxResultsParam != null) {
                try {
                    maxResults = Integer.parseInt(maxResultsParam);
                    result.put(PARAM_MAXRESULTS, maxResults);
                } catch (NumberFormatException ex) {
                }
            }
            List<Hit> results = new ArrayList<>(maxResults);
            engine.results(0,
                    numResults > maxResults ? maxResults : numResults, results);
            JSONArray resultsArray = new JSONArray();
            for (Hit hit : results) {
                JSONObject hitJson = new JSONObject();
                hitJson.put(ATTRIBUTE_DIRECTORY,
                        JSONObject.escape(hit.getDirectory()));
                hitJson.put(ATTRIBUTE_FILENAME,
                        JSONObject.escape(hit.getFilename()));
                hitJson.put(ATTRIBUTE_LINENO, hit.getLineno());
                hitJson.put(ATTRIBUTE_LINE, conv.encode(hit.getLine()));
                hitJson.put(ATTRIBUTE_PATH, hit.getPath());
                resultsArray.add(hitJson);
            }

            long duration = System.currentTimeMillis() - start;

            result.put(ATTRIBUTE_DURATION, duration);
            result.put(ATTRIBUTE_RESULT_COUNT, results.size());
            result.put(ATTRIBUTE_RESULTS, resultsArray);

            System.out.println(result);
        }
        resp.getWriter().write(result.toString());
    }*/
}

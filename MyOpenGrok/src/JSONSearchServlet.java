//
// Source code recreated from a .class file by IntelliJ IDEA
// (powered by Fernflower decompiler)
//

import java.io.IOException;
import java.net.URLDecoder;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.apache.tools.ant.util.Base64Converter;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.opensolaris.opengrok.search.Hit;
import org.opensolaris.opengrok.search.SearchEngine;

public class JSONSearchServlet extends HttpServlet {
    private static final long serialVersionUID = -1675062445999680962L;
    private static final Base64Converter BASE64CONV = new Base64Converter();
    private static final int MAX_RESULTS = 1000;
    private static final String PARAM_FREETEXT = "freetext";
    private static final String PARAM_DEF = "defs";
    private static final String PARAM_SYMBOL = "refs";
    private static final String PARAM_PATH = "path";
    private static final String PARAM_HIST = "hist";
    private static final String PARAM_START = "start";
    private static final String PARAM_MAXRESULTS = "maxresults";
    private static final String PARAM_PROJECT = "project";
    private static final String PARAM_TYPE = "type";
    private static final String ATTRIBUTE_DIRECTORY = "directory";
    private static final String ATTRIBUTE_FILENAME = "filename";
    private static final String ATTRIBUTE_LINENO = "lineno";
    private static final String ATTRIBUTE_LINE = "line";
    private static final String ATTRIBUTE_PATH = "path";
    private static final String ATTRIBUTE_RESULTS = "results";
    private static final String ATTRIBUTE_DURATION = "duration";
    private static final String ATTRIBUTE_RESULT_COUNT = "resultcount";

    public JSONSearchServlet() {
    }

    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        JSONObject result = new JSONObject();
        SearchEngine engine = new SearchEngine();
        boolean valid = false;
        String freetext = req.getParameter(PARAM_FREETEXT);
        String def = req.getParameter(PARAM_DEF);
        String symbol = req.getParameter(PARAM_SYMBOL);
        String path = req.getParameter(PARAM_PATH);
        String hist = req.getParameter(PARAM_HIST);
        String[] projects = req.getParameterValues(PARAM_PROJECT);
        String type = req.getParameter(PARAM_TYPE);
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

        if (type != null) {
            type = URLDecoder.decode(type);
            engine.setType(type);
            valid = true;
            result.put(PARAM_TYPE, type);
        }

        if (valid) {
            try {
                long start = System.currentTimeMillis();
                int numResults;
                if (projects != null && projects.length != 0) {
                    numResults = engine.search(req, projects);
                } else {
                    numResults = engine.search(req);
                }

                int pageStart = getIntParameter(req, "start", 0);
                Integer maxResultsParam = getIntParameter(req, "maxresults", (Integer)null);
                int maxResults = maxResultsParam == null ? 1000 : maxResultsParam;
                if (maxResultsParam != null) {
                    result.put("maxresults", maxResults);
                }

                List<Hit> results = new ArrayList(maxResults);
                engine.results(pageStart, numResults > maxResults ? maxResults : numResults, results);
                JSONArray resultsArray = new JSONArray();
                Iterator var21 = results.iterator();

                while(var21.hasNext()) {
                    Hit hit = (Hit)var21.next();
                    JSONObject hitJson = new JSONObject();
                    hitJson.put("directory", JSONObject.escape(hit.getDirectory()));
                    hitJson.put("filename", JSONObject.escape(hit.getFilename()));
                    hitJson.put("lineno", hit.getLineno());
                    hitJson.put("line", BASE64CONV.encode(hit.getLine()));
                    hitJson.put("path", hit.getPath());
                    resultsArray.add(hitJson);
                }

                long duration = System.currentTimeMillis() - start;
                result.put("duration", duration);
                result.put("resultcount", results.size());
                result.put("results", resultsArray);
                resp.setContentType("application/json");
                resp.getWriter().write(result.toString());
            } finally {
                engine.destroy();
            }
        }
    }

    private static Integer getIntParameter(HttpServletRequest request, String paramName, Integer defaultValue) {
        String paramValue = request.getParameter(paramName);
        if (paramValue == null) {
            return defaultValue;
        } else {
            try {
                return Integer.valueOf(paramValue);
            } catch (NumberFormatException var5) {
                return defaultValue;
            }
        }
    }
}

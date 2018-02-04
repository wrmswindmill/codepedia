import org.opensolaris.opengrok.analysis.Definitions;
import org.opensolaris.opengrok.index.IndexDatabase;
import org.opensolaris.opengrok.web.PageConfig;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.File;
import java.io.IOException;


public class NavigationServlet extends HttpServlet {
    //获取文件的
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)  throws ServletException, IOException {
        String out="";
        try{
            PageConfig cfg = PageConfig.get(req);
            File resourceFile = cfg.getResourceFile();
            Definitions defs = IndexDatabase.getDefinitions(resourceFile);
            out=new Navigation().writeSymbolTable(defs);
        }catch (Exception e) {
            out = "{status:\"failed\",msg:\"parse failed\"}";
        }finally {
            resp.getOutputStream().write( (out).getBytes("utf-8") );
        }

    }
}

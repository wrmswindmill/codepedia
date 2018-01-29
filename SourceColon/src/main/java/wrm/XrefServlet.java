package wrm;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import org.watermint.sourcecolon.org.opensolaris.opengrok.configuration.RuntimeEnvironment;
import org.watermint.sourcecolon.org.opensolaris.opengrok.web.PageConfig;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.awt.*;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

public class XrefServlet extends HttpServlet {

    String head="";

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        doPost(req, resp);
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        RuntimeEnvironment env = RuntimeEnvironment.getInstance();
        File root = new File(env.getDataRootFile(), "index");
        System.out.println(env.getDataRootPath());

        String out= getFileContent(req);
        out = dealContent(out);
        resp.setHeader("content-type", "text/html;charset=utf-8");
        resp.getOutputStream().write(("<pre class=\"prettyprint linenums\"><code>").getBytes("utf-8"));
        resp.getOutputStream().write((out).getBytes("utf-8"));
        resp.getOutputStream().write(("</code></pre>").getBytes("utf-8"));
    }

    public String getFileContent(HttpServletRequest req){
        head="/home/wrm/.sourcecolon/data";
        String uri=req.getRequestURI();
        uri=uri.replace("myxref","xref");
        String path = head+uri+".gz";
        System.out.println(path);

        String out=PageConfig.get(req).fileContents(new File(path));
        if("".equals(out) || out==null){
           return null;
        }
        return out;
    }

    //对调用opengrok获取的html内容进行修改,变为codepedia处理的html
    public String dealContent(String html){
        //jsoup会有bug,这两行是相对应的处理代码
        html=html.replaceAll("\n","x78fa12@!");
        html=html.replaceAll("\t","x78fa13@!");

        //修改的內容只针对<a>标签
        Document doc = Jsoup.parse(html);
        Elements links = doc.getElementsByTag("a");
        int i=0;
        while(i<links.size()){
            Element link=links.get(i);
            //将href标签设置为#,将Onclick中的内容设置为例如search_symbol("def","Date")的形式
            if(link.hasAttr("href")) {
                link.attr("onClick","search_symbol("+getOnclickContext(link)+")");
                link.attr("href","#");
            }
            i++;
        }

        return doc.html().replaceAll("x78fa12@!","\n").replaceAll("x78fa13@!","\t");
    }


    public String getOnclickContext(Element link) {
        if(link.attr("href").split("[?]").length>1) {
            String[] argPairs = link.attr("href").split("[?]")[1].split("&");
            StringBuffer context = new StringBuffer();
            for (int i = 0; i < argPairs.length; i++) {
                String[] arg_value=argPairs[i].split("=");
                context.append("\"").append(arg_value[0]).append("\"");
                if(arg_value.length==2) {
                    context.append(",\"").append(arg_value[1]).append("\"");
                }
            }
//            System.out.println(context.toString());
            return context.toString();
        }
        return null;
    }


    //        int i=0;
//        while(i<links.size()){
//            Element link=links.get(i);
//
//            if("xmt".equals(link.attr("class"))){
//                Element newlink=links.get(++i);
//                if(newlink.hasAttr("href")){
//                    String newhref=newlink.attr("href").replace("refs","defs");
//                    newlink.attr("href",newhref);
//                }
//                continue;
//            } //1.將所有field字段的<a>去掉
//            else if(link.hasAttr("href") && link.attr("href").contains("refs")){
//                link.removeAttr("href");
//                System.out.println(link.attr("href"));
//            }
//            i++;
//        }
//        return doc.html().replaceAll("x78fa12@!","\n").replaceAll("x78fa13@!","\t");


}

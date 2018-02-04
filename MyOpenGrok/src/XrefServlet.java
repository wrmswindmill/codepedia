import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import org.opensolaris.opengrok.configuration.RuntimeEnvironment;
import org.opensolaris.opengrok.web.Util;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.OutputStreamWriter;

public class XrefServlet extends HttpServlet {


    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        doPost(req, resp);
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {

        RuntimeEnvironment env = RuntimeEnvironment.getInstance();
//        File root = new File(env.getDataRootFile(), "index");

        String out= getFileContent(env.getDataRootPath(),req);
        out = dealContent(out);
        resp.setHeader("content-type", "text/html;charset=utf-8");
        resp.getOutputStream().write(("<pre class=\"prettyprint linenums\"><code>").getBytes("utf-8"));
        resp.getOutputStream().write((out).getBytes("utf-8"));
        resp.getOutputStream().write(("</code></pre>").getBytes("utf-8"));
    }

    //该方法获取文件对应的代码段区域(html格式的代码)
    //实际上文件就储存在<opengrok-homedir>/data/下面
    public String getFileContent(String head,HttpServletRequest req){
        String uri=req.getRequestURI();
        uri=uri.replace("myxref","xref");
        String path = head+uri+".gz";
        System.out.println(path);

        String out=fileContents(new File(path));
        if("".equals(out) || out==null){
           return null;
        }
        return out;
    }

    public String fileContents(File dataFile) {
        ByteArrayOutputStream content = new ByteArrayOutputStream();
        OutputStreamWriter writer = new OutputStreamWriter(content);
        System.out.println(dataFile.getAbsolutePath());

        Util.dump(writer, dataFile, dataFile.getName().endsWith(".gz"));
        try {
            writer.flush();
            return content.toString();
        } catch (IOException e) {
            e.printStackTrace();
            return "";
        }
    }


    //对调用opengrok获取的html内容进行修改,变为符合codepedia需求的html
    public String dealContent(String html){
        //jsoup会有bug,会将\t以及\n的html代码处理
        //这两行是相对应的处理代码,首先将原html中的\n和\t转义,处理完之后再转义回来
        html=html.replaceAll("\n","x78!f");
        html=html.replaceAll("\t","c82d@");

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

        return doc.html().replaceAll("x78!f","\n").replaceAll("c82d@","\t");
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

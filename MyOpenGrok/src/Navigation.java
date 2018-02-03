import org.opensolaris.opengrok.analysis.Definitions;
import org.opensolaris.opengrok.web.Util;

import java.io.IOException;
import java.util.*;

public class Navigation {

    public String writeSymbolTable(Definitions defs) throws IOException {
        if (defs == null) {
            // No definitions, no symbol table to write
            return null;
        }

        // We want the symbol table to be sorted
        Comparator<Definitions.Tag> cmp = new Comparator<Definitions.Tag>() {
            @Override
            public int compare(Definitions.Tag tag1, Definitions.Tag tag2) {
                // Order by symbol name, and then by line number if multiple
                // definitions use the same symbol name
                int ret = tag1.symbol.compareTo(tag2.symbol);
                if (ret == 0) {
                    ret = tag1.line - tag2.line;
                }
                return ret;
            }
        };

        Map<String, SortedSet<Definitions.Tag>> symbols
                = new HashMap<>();

        for (Definitions.Tag tag : defs.getTags()) {
            Style style = getStyle(tag.type);
            if (style != null && style.title != null) {
                SortedSet<Definitions.Tag> tags = symbols.get(style.name);
                if (tags == null) {
                    tags = new TreeSet<>(cmp);
                    symbols.put(style.name, tags);
                }
                tags.add(tag);
            }
        }

        StringBuffer out = new StringBuffer();

        //TODO try to get rid of included js scripts generated from here (all js should ideally be in util)
//        out.append("<script type=\"text/javascript\">/* <![CDATA[ */\n");
//        out.append("function get_sym_list(){return [");

        boolean first = true;
        for (Style style : DEFINITION_STYLES) {
            SortedSet<Definitions.Tag> tags = symbols.get(style.name);
            if (tags != null) {
                if (!first) {
                    out.append(',');
                }
                out.append("[\"");
                out.append(style.title);
                out.append("\",\"");
                out.append(style.ssClass);
                out.append("\",[");

                boolean firstTag = true;
                for (Definitions.Tag tag : tags) {
                    if (!firstTag) {
                        out.append(',');
                    }
                    out.append('[');
                    out.append(Util.jsStringLiteral(tag.symbol));
                    out.append(',');
                    out.append(Integer.toString(tag.line));
                    out.append(']');
                    firstTag = false;
                }
                out.append("]]");
                first = false;
            }
        }
        return out.toString();
        /* no LF intentionally - xml is whitespace aware ... */
//        out.append("];} /* ]]> */</script>");
    }

    private static final Style[] DEFINITION_STYLES = {
            new Style("macro", "xm", "Macro"),
            new Style("argument", "xa", null),
            new Style("local", "xl", null),
            new Style("variable", "xv", "Variable"),
            new Style("class", "xc", "Class"),
            new Style("package", "xp", "Package"),
            new Style("interface", "xi", "Interface"),
            new Style("namespace", "xn", "Namespace"),
            new Style("enumerator", "xer", null),
            new Style("enum", "xe", "Enum"),
            new Style("struct", "xs", "Struct"),
            new Style("typedefs", "xts", null),
            new Style("typedef", "xt", "Typedef"),
            new Style("union", "xu", null),
            new Style("field", "xfld", null),
            new Style("member", "xmb", null),
            new Style("function", "xf", "Function"),
            new Style("method", "xmt", "Method"),
            new Style("subroutine", "xsr", "Subroutine"),
    };

    private static class Style {

        /**
         * Name of the style definition as given by CTags.
         */
        final String name;
        /**
         * Class name used by the style sheets when rendering the xref.
         */
        final String ssClass;
        /**
         * The title of the section to which this type belongs, or {@code null}
         * if this type should not be listed in the navigation panel.
         */
        final String title;

        /**
         * Construct a style description.
         */
        Style(String name, String ssClass, String title) {
            this.name = name;
            this.ssClass = ssClass;
            this.title = title;
        }
    }

    private Style getStyle(String type) {
        for (Style style : DEFINITION_STYLES) {
            if (type.startsWith(style.name)) {
                return style;
            }
        }
        return null;
    }
}

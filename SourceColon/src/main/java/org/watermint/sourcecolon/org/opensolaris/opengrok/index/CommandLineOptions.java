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
 * Copyright (c) 2008, 2011, Oracle and/or its affiliates. All rights reserved.
 *
 * Portions Copyright 2011 Jens Elkner.
 * Portions Copyright (c) 2013 Takayuki Okazaki.
 */
package org.watermint.sourcecolon.org.opensolaris.opengrok.index;

import org.watermint.sourcecolon.org.opensolaris.opengrok.util.IOUtils;

import java.io.PrintWriter;
import java.io.StringWriter;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

public class CommandLineOptions {

    private static final String ON_OFF = "on/off";
    private static final String NUMBER = "number";

    static class Option {

        char option;
        String argument;
        String description;

        public Option(char opt, String arg, String desc) {
            option = opt;
            argument = arg;
            description = desc;
        }

        public String getUsage() {
            StringBuilder sb = new StringBuilder();
            sb.append('-');
            sb.append(option);
            if (argument != null) {
                sb.append(' ');
                sb.append(argument);
            }
            sb.append("\n\t");
            sb.append(description);

            return sb.toString();
        }
    }

    private final List<Option> options;

    public CommandLineOptions() {
        options = new ArrayList<>();
        options.add(new Option('?', null, "Help"));
        options.add(new Option('A', "ext:analyzer", "Files with the named extension should be analyzed with the specified class"));
        options.add(new Option('a', ON_OFF, "Allow or disallow leading wildcards in a search"));
        options.add(new Option('C', null, "Print per project percentage progress information(I/O extensive, since one read through dir structure is made before indexing, needs -v, otherwise it just goes to the log)"));
        options.add(new Option('c', "/path/to/ctags", "Path to Exuberant Ctags from http://ctags.sf.net by default takes the Exuberant Ctags in PATH."));
        options.add(new Option('d', "/path/to/data/root", "The directory where OpenGrok stores the generated data"));
        options.add(new Option('e', null, "Economical - consumes less disk space. It does not generate hyper text cross reference files offline, but will do so on demand - which could be sightly slow."));
        options.add(new Option('I', "pattern", "Only files matching this pattern will be examined (supports wildcards, example: -I *.java -I *.c)"));
        options.add(new Option('i', "pattern", "Ignore the named files or directories (supports wildcards, example: -i *.so -i *.dll)"));
        options.add(new Option('l', ON_OFF, "Turn on/off locking of the Lucene database during index generation"));
        options.add(new Option('m', NUMBER, "The maximum words to index in a file"));
        options.add(new Option('N', "/path/to/symlink", "Allow this symlink to be followed. Option may be repeated."));
        options.add(new Option('n', null, "Do not generate indexes, but process all other command line options"));
        options.add(new Option('P', null, "Generate a project for each of the top-level directories in source root"));
        options.add(new Option('p', "/path/to/default/project", "This is the path to the project that should be selected by default in the web application(when no other project set either in cookie or in parameter). You should strip off the source root."));
        options.add(new Option('Q', ON_OFF, "Turn on/off quick context scan. By default only the first 32k of a file is scanned, and a '[..all..]' link is inserted if the file is bigger. Activating this may slow the server down (Note: this is setting only affects the web application)"));
        options.add(new Option('q', null, "Run as quietly as possible"));
        options.add(new Option('s', "/path/to/source/root", "The root directory of the source tree"));
        options.add(new Option('T', NUMBER, "The number of threads to use for index generation. By default the number of threads will be set to the number of available CPUs"));
        options.add(new Option('t', NUMBER, "Default tabsize to use (number of spaces per tab character)"));
        options.add(new Option('V', null, "Print version and quit"));
        options.add(new Option('v', null, "Print progress information as we go along"));
        options.add(new Option('W', "/path/to/configuration", "Write the current configuration to the specified file (so that the web application can use the same configuration"));
        options.add(new Option('w', "webapp-context", "Context of webapp. Default is /source. If you specify a different name, make sure to rename source.war to that name."));
        options.add(new Option('X', "url:suffix", "URL Suffix for the user Information provider. Default: \"\""));
    }

    public String getCommandString() {
        StringBuilder sb = new StringBuilder();
        for (Option o : options) {
            sb.append(o.option);
            if (o.argument != null) {
                sb.append(':');
            }
        }
        return sb.toString();
    }

    public String getCommandUsage(char c) {
        for (Option o : options) {
            if (o.option == c) {
                return o.getUsage();
            }
        }

        return null;
    }

    public String getUsage() {
        StringWriter wrt = new StringWriter();
        PrintWriter out = new PrintWriter(wrt);

        out.println("Usage: opengrok.jar [options]");
        for (Option o : options) {
            out.println(o.getUsage());
        }

        out.flush();
        IOUtils.close(out);

        return wrt.toString();
    }

    /**
     * Not intended for normal use, but for the JUnit test suite to validate
     * that all options contains a description :-)
     *
     * @return an iterator to iterate through all of the command line options
     */
    Iterator<Option> getOptionsIterator() {
        return options.iterator();
    }
}

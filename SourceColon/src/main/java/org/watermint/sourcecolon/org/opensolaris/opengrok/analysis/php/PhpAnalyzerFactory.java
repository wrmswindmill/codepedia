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
 * Portions Copyright (c) 2013 Takayuki Okazaki.
 */

package org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.php;

import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.Definitions;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.FileAnalyzer;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.FileAnalyzer.Genre;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.FileAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.configuration.Project;

import java.io.IOException;
import java.io.Reader;
import java.io.Writer;

public class PhpAnalyzerFactory extends FileAnalyzerFactory {

    private static final String[] SUFFIXES = {
            "PHP",
            "PHP3",
            "PHP4",
            "PHP5",
            "PHPS",
            "PHTML"
    };
    private static final String[] MAGICS = {
            "#!/usr/bin/env php",
            "#!/usr/bin/php",
            "#!/bin/php",
            "<?php"
    };

    public PhpAnalyzerFactory() {
        super(null, SUFFIXES, MAGICS, null, "text/plain", Genre.PLAIN);
    }

    @Override
    protected FileAnalyzer newAnalyzer() {
        return new PhpAnalyzer(this);
    }

    @Override
    public void writeXref(Reader in, Writer out, Definitions defs, Project project)
            throws IOException {
        PhpAnalyzer.writeXref(in, out, defs, project);
    }
}

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
 * Copyright (c) 2007, 2010, Oracle and/or its affiliates. All rights reserved.
 * Portions Copyright (c) 2013 Takayuki Okazaki.
 */

package org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.plain;

import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.AnalyzerGuru;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.Definitions;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.FileAnalyzer;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.FileAnalyzer.Genre;
import org.watermint.sourcecolon.org.opensolaris.opengrok.analysis.FileAnalyzerFactory;
import org.watermint.sourcecolon.org.opensolaris.opengrok.configuration.Project;

import java.io.IOException;
import java.io.InputStream;
import java.io.Reader;
import java.io.Writer;

public final class PlainAnalyzerFactory extends FileAnalyzerFactory {

    private static final Matcher MATCHER = new Matcher() {
        public FileAnalyzerFactory isMagic(byte[] content, InputStream in)
                throws IOException {
            if (isPlainText(content)) {
                return DEFAULT_INSTANCE;
            } else {
                return null;
            }
        }

        /**
         * Check whether the byte array contains plain text. First, check
         * assuming US-ASCII encoding. Then, if unsuccessful, try to
         * strip away Unicode byte-order marks and try again.
         */
        private boolean isPlainText(byte[] content) throws IOException {
            String ascii = new String(content, "US-ASCII");
            if (isPlainText(ascii)) {
                return true;
            }

            String noBOM = AnalyzerGuru.stripBOM(content);
            return (noBOM != null) && isPlainText(noBOM);
        }

        /**
         * Check whether the string only contains plain ASCII characters.
         */
        private boolean isPlainText(String str) {
            for (int i = 0; i < str.length(); i++) {
                char b = str.charAt(i);
                if ((b >= 32 && b < 127) || // ASCII printable characters
                        (b == 9) || // horizontal tab
                        (b == 10) || // line feed
                        (b == 12) || // form feed
                        (b == 13)) {        // carriage return
                    // is plain text so far, go to next byte
                    continue;
                } else {
                    // 8-bit values or unprintable control characters,
                    // probably not plain text
                    return false;
                }
            }
            return true;
        }
    };

    public static final PlainAnalyzerFactory DEFAULT_INSTANCE =
            new PlainAnalyzerFactory();

    private PlainAnalyzerFactory() {
        super(null, null, null, MATCHER, "text/plain", Genre.PLAIN);
    }

    @Override
    protected FileAnalyzer newAnalyzer() {
        return new PlainAnalyzer(this);
    }

    @Override
    public void writeXref(Reader in, Writer out, Definitions defs, Project project)
            throws IOException {
        PlainAnalyzer.writeXref(in, out, defs, project);
    }
}

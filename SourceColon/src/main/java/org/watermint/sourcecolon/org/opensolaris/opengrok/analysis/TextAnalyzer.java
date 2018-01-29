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

package org.watermint.sourcecolon.org.opensolaris.opengrok.analysis;

import com.ibm.icu.text.CharsetDetector;
import com.ibm.icu.text.CharsetMatch;
import org.apache.lucene.document.Document;
import org.watermint.sourcecolon.org.opensolaris.opengrok.util.IOUtils;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;

public abstract class TextAnalyzer extends FileAnalyzer {
    public TextAnalyzer(FileAnalyzerFactory factory) {
        super(factory);
    }

    public final void analyze(Document doc, InputStream in) throws IOException {
        analyze(doc, IOUtils.readerWithCharsetDetect(in));
    }

    protected abstract void analyze(Document doc, Reader reader) throws IOException;
}

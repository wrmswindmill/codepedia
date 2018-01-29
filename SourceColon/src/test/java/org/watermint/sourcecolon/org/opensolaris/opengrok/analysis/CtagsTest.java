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
 * Copyright (c) 2010, 2011, Oracle and/or its affiliates. All rights reserved.
 * Portions Copyright (c) 2013 Takayuki Okazaki.
 */

package org.watermint.sourcecolon.org.opensolaris.opengrok.analysis;

import java.io.File;
import java.io.IOException;

import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.watermint.sourcecolon.org.opensolaris.opengrok.configuration.RuntimeEnvironment;
import org.watermint.sourcecolon.org.opensolaris.opengrok.util.TestRepository;

import static org.junit.Assert.*;

/**
 * @author Lubos Kosco
 */
public class CtagsTest {
    private static Ctags ctags;
    private static TestRepository repository;
    private static boolean skipTest = false;

    public CtagsTest() {
    }

    @BeforeClass
    public static void setUpClass() throws Exception {
        skipTest = !RuntimeEnvironment.getInstance().validateExuberantCtags();
        if (!skipTest) {
            ctags = new Ctags();
            ctags.setBinary(RuntimeEnvironment.getInstance().getCtags());
            repository = new TestRepository();
            repository.create(CtagsTest.class.getResourceAsStream(
                    "/org/watermint/sourcecolon/org/opensolaris/opengrok/index/source.zip"));
        }
    }

    @AfterClass
    public static void tearDownClass() throws Exception {
        if (!skipTest) {
            ctags.close();
            ctags = null;
            repository.destroy();
        }
    }

    @Before
    public void setUp() throws IOException {
    }

    @After
    public void tearDown() {
    }

    /**
     * Helper method that gets the definitions for a file in the repository.
     *
     * @param fileName file name relative to source root
     * @return the definitions found in the file
     */
    private static Definitions getDefs(String fileName) throws Exception {
        String path = repository.getSourceRoot() + File.separator
                + fileName.replace('/', File.separatorChar);
        return ctags.doCtags(new File(path).getAbsolutePath() + "\n");
    }

    /**
     * Test of doCtags method, of class Ctags.
     */
    @Test
    public void testDoCtags() throws Exception {
        if (skipTest) {
            return;
        }
        Definitions result = getDefs("bug16070/arguments.c");
        assertEquals(13, result.numberOfSymbols());
    }

    /**
     * Test that we don't get many false positives in the list of method
     * definitions for Java files. Bug #14924.
     */
    @Test
    public void bug14924() throws Exception {
        if (skipTest) {
            return;
        }

        // Expected method names found in the file
        String[] names = {"ts", "classNameOnly", "format"};
        // Expected line numbers for the methods
        int[] lines = {44, 48, 53};

        Definitions result = getDefs("bug14924/FileLogFormatter.java");
        int count = 0;
        for (Definitions.Tag tag : result.getTags()) {
            if (tag.type.startsWith("method")) {
                assertTrue("too many methods", count < names.length);
                assertEquals("method name", names[count], tag.symbol);
                assertEquals("method name", lines[count], tag.line);
                count++;
            }
        }
        assertEquals("method count", names.length, count);
    }
}

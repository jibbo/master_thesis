/**
 * The ARTist Project (https://artist.cispa.saarland)
 * <p>
 * Copyright (C) 2017 CISPA (https://cispa.saarland), Saarland University
 * <p>
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * <p>
 * http://www.apache.org/licenses/LICENSE-2.0
 * <p>
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * @author "Oliver Schranz <oliver.schranz@cispa.saarland>"
 * @author "Sebastian Weisgerber <weisgerber@cispa.saarland>"
 */
package saarland.cispa.artist.codelib;

import android.database.Cursor;
import android.database.SQLException;
import android.database.sqlite.SQLiteCursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteException;
import android.util.Log;

import java.math.BigInteger;
import java.nio.ByteBuffer;
import java.security.SecureRandom;
import java.util.ArrayList;
import java.util.Objects;
import java.util.Random;

public class CodeLib {

    // Instance variable for singleton usage ///////////////////////////////////////////////////////
    public static CodeLib INSTANCE = new CodeLib();

    // <Constants> /////////////////////////////////////////////////////////////////////////////////
    private static final String TAG = "ArtistCodeLib";
    private static final String VERSION = TAG + " # 1.0.0";

    final String MSG_NOT_FOUND = "<Not Found>";
    // </Constants> ////////////////////////////////////////////////////////////////////////////////

    /**
     * Static Class Constructor
     */
    static {
        // <Code>
    }

    /**
     * Private Class Constructor
     * => Forbidden Class Initialisation (Singleton)
     */
    private CodeLib() {
        Log.v(TAG, TAG + " CodeLib() " + VERSION);
    }

    /**
     * Get the name of the calling method
     * <p>
     * The name is probed from the current Thread's stacktrace.
     *
     * @return the name of the calling method
     */
    private String getCallingMethodName() {
        // CallStack depth of calling function.
        final int CALLING_METHOD_STACK_LEVEL = 4;

        final StackTraceElement[] stackTrace = Thread.currentThread().getStackTrace();
        String callingMethodName;
        try {
            final StackTraceElement callingMethod = stackTrace[CALLING_METHOD_STACK_LEVEL];
            callingMethodName = callingMethod.toString();
        } catch (final NullPointerException e) {
            callingMethodName = MSG_NOT_FOUND;
        } catch (final ArrayIndexOutOfBoundsException e) {
            callingMethodName = MSG_NOT_FOUND;
        }
        return callingMethodName;
    }

    /**
     * Tracelog method, prints the method name of the calling method.
     */
    public void traceLog() {
        final String callingMethodName = getCallingMethodName();
        Log.d(TAG, "Caller -> " + callingMethodName);
    }

    /**
     * Logs the paramenter to the android logger.
     *
     * @param value parameter which gets logged
     */
    public void logBoolean(final boolean value) {
        Log.d(TAG, "logBoolean() #1: " + value);
    }

    /**
     * Logs the paramenter to the android logger.
     *
     * @param value parameter which gets logged
     */
    public void logChar(final char value) {
        Log.d(TAG, "logChar()    #1: " + value);
    }

    /**
     * Logs the paramenter to the android logger.
     *
     * @param value parameter which gets logged
     */
    public void logInteger(final int value) {
        Log.d(TAG, "logInteger() #1: " + value);
    }

    /**
     * @param value  parameter which gets logged
     * @param value2 parameter which gets logged
     */
    public void logInteger(final int value, final int value2) {
        Log.d(TAG, "logInteger() #1: " + value + " #2: " + value2);
    }

    /**
     * Logs parameter to the console.
     * <p>
     * It is selectable if the calling method's name should get logged.
     *
     * @param logWithTrace Set to true if calling method name should get logged
     * @param value        parameter which gets logged
     */
    public void logIntegerTrace(final boolean logWithTrace, final int value) {
        if (logWithTrace) {
            Log.d(TAG, "logInteger() #1: " + value);
            Log.d(TAG, "> Caller -> " + getCallingMethodName());
        } else {
            Log.d(TAG, "logInteger() #1: " + value);
        }
    }

    /**
     * Logs the paramenter to the android logger.
     *
     * @param value parameter
     */
    public void logLong(final long value) {
        Log.d(TAG, "logLong()    #1: " + value);
    }

    /**
     * Logs the paramenter to the android logger.
     *
     * @param value parameter
     */
    public void logFloat(final float value) {
        Log.d(TAG, "logFloat()   #1: " + value);
    }

    /**
     * Logs the paramenter to the android logger.
     *
     * @param value parameter
     */
    public void logDouble(final double value) {
        Log.w(TAG, "logDouble()  #1: " + value);
    }

    /**
     * **********************************************************************************************
     * DEVARTIST                                                                 *
     * **********************************************************************************************
     */

    private static ArrayList<String> sqlQueryComponents = new ArrayList<>();

    public void addSqlQueryComponent(int component) {
        sqlQueryComponents.add(component + "");
        Log.w(TAG, "[TC][QUERY] addSqlQueryComponent: int->" + component);
    }

    public void addSqlQueryComponent(double component) {
        sqlQueryComponents.add(component + "");
        Log.w(TAG, "[TC][QUERY] addSqlQueryComponent: double->" + component);
    }

    public void addSqlQueryComponent(float component) {
        sqlQueryComponents.add(component + "");
        Log.w(TAG, "[TC][QUERY] addSqlQueryComponent: float->" + component);
    }

    public void addSqlQueryComponent(boolean component) {
        sqlQueryComponents.add(component + "");
        Log.w(TAG, "[TC][QUERY] addSqlQueryComponent: bool->" + component);
    }

    public void addSqlQueryComponent(long component) {
        sqlQueryComponents.add(component + "");
        Log.w(TAG, "[TC][QUERY] addSqlQueryComponent: long->" + component);
    }

    public void addSqlQueryComponent(char component) {
        sqlQueryComponents.add(String.valueOf(component).toLowerCase());
        Log.w(TAG, "[TC][QUERY] addSqlQueryComponent: char->" + component);
    }

    public void addSqlQueryComponent(byte component) {
        sqlQueryComponents.add(new String(new byte[]{component}));
        Log.w(TAG, "[TC][QUERY] addSqlQueryComponent: byte->" + component);
    }

    public void addSqlQueryComponent(short component) {
        sqlQueryComponents.add(component + "");
        Log.w(TAG, "[TC][QUERY] addSqlQueryComponent: short->" + component);
    }

    public void addSqlQueryComponent(Object component) {
        if (component != null) {
            String componentString = component.toString().toLowerCase();
            sqlQueryComponents.add(componentString);
            Log.w(TAG, "[TC][QUERY] addSqlQueryComponent: obj->" + componentString);
        } else {
            Log.w(TAG, "[TC][QUERY] addSqlQueryComponent: obj-> NULL ");
        }
    }

    public Cursor patchedRawQuery(SQLiteDatabase database, String query, String[] sqlArgs) {
        StaticSqlInjectionAnalyzer.AnalysisResult result = analyseQuery(query, sqlArgs);
        Log.w(TAG, "[TC][QUERY] Analysis result: " + result.toString());
        String patchedQuery = patchQuery(database, sqlArgs, result, query);
        if (patchedQuery.equals(query)) {
            Log.w(TAG, "[TC][QUERY][SAFE] running query:" + query);
        } else {
            Log.w(TAG, "[TC][QUERY] old query: " + query);
            Log.w(TAG, "[TC][QUERY][PATCHED] patched query: " + patchedQuery);
        }
        try {
            return database.rawQuery(patchedQuery, sqlArgs);
        } catch (SQLException e) {
            return database.rawQuery("", null);
        }
    }

    private String patchQuery(SQLiteDatabase database, String[] sqlArgs, StaticSqlInjectionAnalyzer
            .AnalysisResult result, String query) {
        if (result.hasInjection) {
            String patchedSql = "";
            if (result.sqlArgIndex != null) {
                if (sqlArgs != null && sqlArgs.length >= result.sqlArgIndex) {
                    patchedSql = StaticSqlInjectionAnalyzer.patchSqlArgs(query, sqlArgs, result);
                } else if (sqlQueryComponents.size() >= result.sqlArgIndex) {
                    patchedSql = StaticSqlInjectionAnalyzer.patchQueryComponents(query,
                            sqlQueryComponents, result);
                }
            } else if (result.onFullQuery) {
                patchedSql = StaticSqlInjectionAnalyzer.patchFullQuery(query, result);
            }
            return patchedSql;
        }
        return query;
    }

    private StaticSqlInjectionAnalyzer.AnalysisResult analyseQuery(String query, String[] sqlArgs) {
        StaticSqlInjectionAnalyzer.AnalysisResult result;// The raw query must have been used in a good way, but there might be injections
        if (sqlArgs != null && sqlArgs.length > 0) {
            result = StaticSqlInjectionAnalyzer
                    .analyseArgsParams(query, sqlArgs);
        } else if (sqlQueryComponents.size() > 0) {
            // the raw query method is used unsafely, art will aid us
            result = StaticSqlInjectionAnalyzer
                    .analyseQueryComponents(sqlQueryComponents);
        } else {
            // the raw query might me unsafe but art didn't help
            // for some reason.
            result = StaticSqlInjectionAnalyzer.analyseQuery(query);
        }
        return result;
    }

    public String patchHashAlgorithm(String algorithm) {
        algorithm = algorithm.trim().toLowerCase().replace("-", "");
        if (algorithm.contains("sha1") || algorithm.contains("md5")) {
            Log.w(TAG, "[DC][SHA][PATCHED] " + algorithm + "->SHA-256");
            return "SHA-256";
        }
        Log.w(TAG, "[DC][SHA][SAFE] was: " + algorithm);
        return algorithm;
    }

    public SecureRandom getSecureRandom() {
        Log.w(TAG, "[DC][RANDOM][PATCHED] random->SecureRandom");
        return new SecureRandom();
    }

    public SecureRandom getSecureRandom(long seed) {
        Log.w(TAG, "[DC][RANDOM][PATCHED] random(seed)->SecureRandom(seed)");
        ByteBuffer buffer = ByteBuffer.allocate(8);
        buffer.putLong(seed);
        return new SecureRandom(buffer.array());
    }

}

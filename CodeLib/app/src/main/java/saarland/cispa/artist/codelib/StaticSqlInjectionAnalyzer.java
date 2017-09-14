package saarland.cispa.artist.codelib;


import android.util.Log;

import java.util.ArrayList;

/**
 * Created by jibbo on 3/5/17.
 */
class StaticSqlInjectionAnalyzer {
    private static final String TAG = "StaticSqlInjectionAnaly";

    private static final String[] commonAttacks = {
            "--",
            "or 1=1",
            "or '1'='1",
            "or '1' = '1'",
            "union select 1,null,null",
            "%00",
            "/**/",
            "//",
            ";",
            "\"\"=\"\"",
            "''=''",
            "or true"
    };

    static AnalysisResult analyseArgsParams(String query, String[] sqlArgs) {
        if (sqlArgs != null && sqlArgs.length > 0) {
            // first i try just on the parameters
            for (int i = 0; i < sqlArgs.length; i++) {
                String arg = sqlArgs[i].toLowerCase();
                for (String attack : commonAttacks) {
                    attack = attack.toLowerCase();
                    if (trim(arg).contains(trim(attack))) {
                        return new AnalysisResult(true, i, attack.toLowerCase(), false);
                    }
                }
            }
            // then I try on the query when the parameters are injected
            String finalQuery = injectArgsIntoQueryString(query, sqlArgs).toLowerCase();
            for (String attack : commonAttacks) {
                attack = attack.toLowerCase();
                if (trim(finalQuery).contains(trim(attack))) {
                    return new AnalysisResult(true, null, attack, false);
                }
            }
        }
        return new AnalysisResult(false, null, null, true);
    }

    static AnalysisResult analyseQueryComponents(ArrayList<String> components) {
        //Trying to find common SQLI inside the components found by art
        if (components != null && components.size() > 0) {
            for (int i = 0; i < components.size(); i++) {
                String component = components.get(i).toLowerCase();
                for (String attack : commonAttacks) {
                    attack = attack.toLowerCase();
                    if (trim(component).contains(trim(attack))) {
                        return new AnalysisResult(true, i, attack, false);
                    }
                }
            }
        }
        return new AnalysisResult(false, null, null, false);
    }

    static AnalysisResult analyseQuery(String query) {
        //Maybem it's in the query itself for some reason
        for (String attack : commonAttacks) {
            attack = attack.toLowerCase();
            if (trim(query.toLowerCase()).contains(trim(attack))) {
                return new AnalysisResult(true, null, attack, true);
            }
        }
        return new AnalysisResult(false, null, null, true);
    }

    static String injectArgsIntoQueryString(String query, String[] sqlArgs) {
        if (sqlArgs != null && sqlArgs.length > 0) {
            for (String arg : sqlArgs) {
                int index = query.indexOf('?');
                if (index > -1) {
                    String tmp = query.substring(index + 1, query.length());
                    query = query.substring(0, index) + arg + tmp;
                }
            }
        }
        return query;
    }

    static String patchSqlArgs(String query, String[] sqlArgs, AnalysisResult result) {
        if (result.sqlArgIndex != null) {
            if (result.foundInjection != null) {
                // remove the dangerous part from the arguments
                sqlArgs[result.sqlArgIndex] = sqlArgs[result.sqlArgIndex].toLowerCase().replace(result
                        .foundInjection, "");
            }
        }
        query = injectArgsIntoQueryString(query.toLowerCase(), sqlArgs);
        return query;
    }

    static String patchQueryComponents(String query, ArrayList<String> sqlQueryComponents, AnalysisResult result) {
        Log.d(TAG, "patchQueryComponents");
        if (result.foundInjection != null && result.sqlArgIndex != null) {
            // replace in the query the part that is infected with the part that is infected -
            // the dangerous part
            query = query.toLowerCase().replace(result.foundInjection, "");
        }
        return query;
    }

    // the default trim function doesn' t trim
    // the space between quotes.
    private static String trim(String s) {
        return s.replace(" ", "");
    }

    static String patchFullQuery(String query, AnalysisResult result) {
        if (result.foundInjection != null) {
            // I replace just the dangerous part
            query = query.toLowerCase().replace(result.foundInjection, "");
        }
        return query;
    }

    static class AnalysisResult {
        public final boolean hasInjection;
        public final Integer sqlArgIndex;
        public final String foundInjection;
        public final boolean onFullQuery;

        public AnalysisResult(boolean hasInjection,
                              Integer sqlArgIndex,
                              String foundInjection,
                              boolean onFullQuery) {
            this.hasInjection = hasInjection;
            this.sqlArgIndex = sqlArgIndex;
            this.foundInjection = foundInjection;
            this.onFullQuery = onFullQuery;
        }

        @Override
        public String toString() {
            return "AnalysisResult{" +
                    "hasInjection=" + hasInjection +
                    ", sqlArgIndex=" + sqlArgIndex +
                    ", foundInjection='" + foundInjection + '\'' +
                    ", onFullQuery=" + onFullQuery +
                    '}';
        }
    }
}

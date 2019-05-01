package com.example.zl.menurecognitiondemo;

import android.util.Log;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Utile {
    public static String decodeUnicode(String dataStr) {
        Pattern pattern = Pattern.compile("(\\\\u(\\p{XDigit}{4}))");
        if (dataStr == null)
            return "识别失败";
        Matcher matcher = pattern.matcher(dataStr);
        char ch;
        while (matcher.find()) {
            //group 6728
            String group = matcher.group(2);
            //ch:'木' 26408
            ch = (char) Integer.parseInt(group, 16);
            //group1 \u6728
            String group1 = matcher.group(1);
            dataStr = dataStr.replace(group1, ch + "");
        }
        return dataStr;
    }
}

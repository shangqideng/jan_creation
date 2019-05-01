package com.example.zl.menurecognitiondemo;

import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.File;
import java.io.IOException;
import java.util.concurrent.TimeUnit;

import okhttp3.Headers;
import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class HttpClient {
    public static final String TAG = "UploadHelper";
    private static final MediaType MEDIA_TYPE_PNG = MediaType.parse("multipart/form-data");

    public String upload(String imageType,String userPhone,File file,String ip) throws Exception{

        RequestBody fileBody = RequestBody.create(MEDIA_TYPE_PNG, file);

        RequestBody requestBody = new MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("file", "head_image", fileBody)
                .build();

        Request request = new Request.Builder()
                .url(ip)
//                .url("http://192.168.5.113:5050/img_upload")
//                .url("http://192.168.8.122:5050/img_upload")
//                .url("http://192.168.5.116:5050/img_upload")
                .post(requestBody)
                .build();

        Response response;
        OkHttpClient client = new OkHttpClient.Builder()
                //设置服务器响应时间 修正SocketTimeoutException：
                .readTimeout(1000,TimeUnit.SECONDS)
//                .connectTimeout(1000,TimeUnit.SECONDS)
                .build();
        try {
            response = client.newCall(request).execute();
            String jsonString = response.body().string();
            Log.d("xxx",jsonString);
            return jsonString;
        } catch (Exception e) {
        Log.d(TAG,"upload IOException ",e);
    }
        return null;
    }
}

package com.example.zl.menurecognitiondemo;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.AlertDialog;
import android.app.Dialog;
import android.app.ProgressDialog;
import android.content.ContentResolver;
import android.content.ContentValues;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Point;
import android.graphics.drawable.BitmapDrawable;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.os.Handler;
import android.os.Message;
import android.provider.MediaStore;
import android.support.annotation.NonNull;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v4.content.FileProvider;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.method.ScrollingMovementMethod;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import com.alibaba.fastjson.JSON;

import org.json.JSONObject;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.Buffer;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class MainActivity extends AppCompatActivity implements View.OnClickListener {

    private Button button,Rec,select;
    private ImageView imageView;
    private TextView textView;
    private ProgressDialog dialog;

    /**
     * 打开系统相机的requestCode
     */
    private final int IMAGE_RESULT = 0;
    private final int SELECT_PIC_BY_PICK_PHOTO = 1;

    /**
     * 请求权限的requestCode
     */
    private final int PERMISSION_RESULT = 1;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        dialog = new ProgressDialog(this);
        dialog.setMessage("识别中...");
        dialog.setCancelable(false);
        dialog.setCanceledOnTouchOutside(false);

        button = findViewById(R.id.btn);
        Rec = findViewById(R.id.Rec);
        select = findViewById(R.id.select);
        imageView = findViewById(R.id.iv);
        textView = findViewById(R.id.textView);
        textView.setMovementMethod(ScrollingMovementMethod.getInstance());
        textView.setScrollbarFadingEnabled(false);
        button.setOnClickListener(this);
        Rec.setOnClickListener(this);
        select.setOnClickListener(this);
    }

    private String ip_temp = null;
    private String ip = null;
    public void say(View v){
        EditText editText2;
        editText2 =(EditText)findViewById(R.id.editText2);
        ip_temp =editText2.getText().toString();
        ip = "http://"+ip_temp+":5050/img_upload";
        Log.i("**********************", ip);
        if(ip_temp != null){
            Toast.makeText(MainActivity.this, "Connect Successfully ", Toast.LENGTH_SHORT).show();
            dialog.dismiss();
        }
    }


    @Override
    public void onClick(View v) {
        int id = v.getId();
        switch (id) {
            case R.id.btn:
                clickButton();
//                takePhoto();
                break;
            case R.id.Rec:
                dialog.show();
                textView.setText("");
                recognition();
                break;
            case R.id.select:// 相册选择图片
//                Log.i("takepo1","-------------111111111111111111111");
                pickPhoto();
                break;
        }
    }
    String result = null;
    File file = null;
    private static final int COMPLETED = 0;
    @SuppressLint("HandlerLeak")
    private Handler handler;

    {
        handler = new Handler() {
            @Override
            public void handleMessage(Message msg) {
                if (msg.what == COMPLETED) {
                    //设置返回结果dialog
                    Toast.makeText(MainActivity.this, "识别成功", Toast.LENGTH_SHORT).show();
                    setResultDialo(msg);
                   // textView.setText(Utile.decodeUnicode(msg.getData().getString("result")));
                    dialog.dismiss();
                }
                if (msg.what == 0x110) {
                    Toast.makeText(MainActivity.this, "返回数据为空", Toast.LENGTH_SHORT).show();
                    setResultDialo2(msg);
                    dialog.dismiss();
                }
                if (msg.what == 20){
                    Toast.makeText(MainActivity.this, "error", Toast.LENGTH_SHORT).show();
                    setResultDialo1(msg);
                    dialog.dismiss();
                }
            }
        };
    }


    private void setResultDialo(Message msg) {
        List<String> stringList = new ArrayList<>();
        stringList = Arrays.asList(Utile.decodeUnicode(msg.getData().getString("result")).split(" "));
        final AlertDialog resultDialog = new AlertDialog.Builder(this).setItems(stringList.toArray(new CharSequence[stringList.size()]),null).create();
        resultDialog.setTitle("识别结果");
        resultDialog.setButton(Dialog.BUTTON_NEGATIVE, "返回", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                resultDialog.dismiss();
            }
        });
        resultDialog.show();
    }

    private void setResultDialo1(Message msg) {
        List<String> stringList = new ArrayList<>();
        stringList = Arrays.asList(Utile.decodeUnicode(msg.getData().getString("error")).split(" "));
        final AlertDialog resultDialog1 = new AlertDialog.Builder(this).setItems(stringList.toArray(new CharSequence[stringList.size()]),null).create();
        resultDialog1.setButton(Dialog.BUTTON_NEGATIVE, "返回", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                resultDialog1.dismiss();
            }
        });
        resultDialog1.show();
    }

    private void setResultDialo2(Message msg) {
        List<String> stringList = new ArrayList<>();
        stringList = Arrays.asList(Utile.decodeUnicode(msg.getData().getString("backerror")).split(" "));
        final AlertDialog resultDialog2 = new AlertDialog.Builder(this).setItems(stringList.toArray(new CharSequence[stringList.size()]),null).create();
        resultDialog2.setButton(Dialog.BUTTON_NEGATIVE, "返回", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                resultDialog2.dismiss();
            }
        });
        resultDialog2.show();
    }

    private void recognition() {

        Log.i("MainActivity","测试");
        imageView.setDrawingCacheEnabled(true);
        Bitmap bitmap = Bitmap.createBitmap(imageView.getDrawingCache());
        imageView.setDrawingCacheEnabled(false);

        try {
            new Thread(new Runnable(){
                public void run() {
                    try {
                        result = new HttpClient().upload(null,null,file,ip);
//                        Log.i("********************",ip);
                        Log.i("recognition:",result);
                        ResponseResult infoDo = JSON.parseObject(result, ResponseResult.class);
                        Log.i("receive","接收到反馈信息");
                        //处理完成后给handler发送消息
                        if (infoDo.getData().length == 0 ) {        //如果没有数据
                            Message noMsg = new Message();
                            noMsg.what = 0x110;
                            Bundle bundle = new Bundle();
                            bundle.putString("backerror","服务器端没有识别结果，请规范打勾");//往Bundle中存放数据
                            noMsg.setData(bundle);//mes利用Bundle传递数据
                            handler.sendMessage(noMsg);
                            return;
                        }
                        Message msg = new Message();
                        msg.what = COMPLETED;
                        Bundle bundle = new Bundle();
                        if (infoDo.getData().length > 0) {
                            StringBuffer sb = new StringBuffer();
                            for(String s:infoDo.getData()) {
                                sb.append(s+" ");
                            }
                            bundle.putString("result", sb.toString());
                        }
                        else
                            bundle.putString("result",null);//往Bundle中存放数据
                        msg.setData(bundle);//mes利用Bundle传递数据
                        handler.sendMessage(msg);
                    } catch (Exception e) {
                        Message msg1 = new Message();
                        msg1.what = 20;
                        Bundle bundle = new Bundle();
                        bundle.putString("error","error403：服务器无返回值 请检查网络或者规范拍照");//往Bundle中存放数据
                        msg1.setData(bundle);//mes利用Bundle传递数据
                        handler.sendMessage(msg1);
                        Log.i("thread","没有东西");
                    }
                }
            }).start();
        } catch (Exception e) {
            e.printStackTrace();
        }
      //
    }

    /***
     * 从相册中取图片
     */
    private void pickPhoto() {
        Intent intent = new Intent();
        // 如果要限制上传到服务器的图片类型时可以直接写如："image/jpeg 、 image/png等的类型"
        intent.setType("image/*");
        intent.setAction(Intent.ACTION_PICK);
        startActivityForResult(intent, SELECT_PIC_BY_PICK_PHOTO);
//        Log.i("retapo","-------------------------------");
    }


//    public File getFile(Bitmap bitmap) {
//        ByteArrayOutputStream baos = new ByteArrayOutputStream();
//        bitmap.compress(Bitmap.CompressFormat.JPEG, 100, baos);
//
//        File file = new File( Environment.getExternalStorageDirectory(), "m.jpg");
//        try {
//            file.createNewFile();
//            FileOutputStream fos = new FileOutputStream(file);
//            InputStream is = new ByteArrayInputStream(baos.toByteArray());
//            int x = 0;
//            byte[] b = new byte[1024 * 100];
//            while ((x = is.read(b)) != -1) {
//                fos.write(b, 0, x);
//            }
//            fos.close();
//            is.close();
//        } catch (Exception e) {
//            e.printStackTrace();
//        }
//        return file;
//    }
//转jpg就把Bitmap.CompressFormat.PNG改成Bitmap.Compressformat.JPEG

    /**
     * 点击 capture_image button
     */
    private void clickButton() {
        if (!checkPermission(mPermission)) {
            requestPermission(mPermission);
        } else {
            //打开相机
            openCameraForResult();
        }
    }



    /**
     * 读写权限
     */
    private final String mPermission = Manifest.permission.WRITE_EXTERNAL_STORAGE;

    /**
     * 图片存储路径
     */
    private String mImageFilePath;
    private String picturePath;

    /**
     * 构建图片路径
     * 将图片保存在Environment.getExternalStorageDirectory()+"/rflash"+"/my.jpg"
     */
    private void createImageFilePath() {
        File file = new File(Environment.getExternalStorageDirectory().getAbsolutePath() + File.separator + "rflash" );// 图片存放路径
//        File file = new File(Environment.getExternalStorageDirectory().getAbsolutePath() + File.separator + "DCIM"+ File.separator + "Camera" );// 图片存放路径
        File list[] = file.listFiles();
        String name = new String("temporarypciture"+list.length+".jpg");
        mImageFilePath = Environment.getExternalStorageDirectory().getAbsolutePath() + File.separator +"rflash"+ File.separator+ name;
        Log.i("root",mImageFilePath+"*******************");
    }

    /**
     * 获取图片uri
     *
     * @return
     */
    private Uri getImageUri() {
        File file = new File(mImageFilePath);
        //###下面代码有些手机需要(如：小米手机)###
        //可以试下去掉下面的代码在小米手机上报什么错
        File parentFile = file.getParentFile();
        //去创建图片存放的父路径
        if (!parentFile.exists()){
            parentFile.mkdirs();
        }
        //###上面面代码有些手机需要(如：小米手机)###
        Uri imageUri;
        if (Build.VERSION.SDK_INT <= Build.VERSION_CODES.N) {
            //N以前
            imageUri = Uri.fromFile(file);
        } else {
            //N以后，通过FileProvider生成
            //特别地，第二个参数authority对应AndroidManifest.xml下provider标签里面的authorities值。
            //我直接使用的application_id
            imageUri = FileProvider.getUriForFile(this, BuildConfig.APPLICATION_ID, file);
            Log.i("---", imageUri.toString());
            //打印结果
            //I/---: content://com.rflash.captrueimage03/image/my.jpg
        }
        return imageUri;
    }

    /**
     * 检查权限是否申请
     *
     * @param permission 权限
     * @return true ：权限已申请
     */
    private boolean checkPermission(String permission) {
        //是否申请权限
        boolean hasPermission = false;
        //通过api去校验权限是否申请，返回判断标志
        int i = ContextCompat.checkSelfPermission(this, permission);
        if (PackageManager.PERMISSION_GRANTED == i) {
            //PERMISSION_GRANTED表示权限已申请
            hasPermission = true;
        } else if (PackageManager.PERMISSION_DENIED == i) {
            //PERMISSION_DENIED表示权限未申请
            hasPermission = false;
        }
        return hasPermission;

    }


    /**
     * 请求权限
     */
    private void requestPermission(String... permission) {
        if (ActivityCompat.shouldShowRequestPermissionRationale(this, permission[0])) {
            //shouldShowRequestPermissionRationale()方法解释
            //1.第一次请求该权限，返回false
            //2.请求过该权限并被用户拒绝，返回true
            //3.请求过该权限，但用户拒绝的时候勾选不再提醒，返回false。
            //总结一下，这个方法的目的：就是说去告诉用户，为什么需要用户同意该权限。
            //todo 所以这里可以给一个ui提示用户同意权限的好处。
            //我这里只是toast。可以理解为伪代码，只是提供一种思路
            Toast.makeText(this, "求求你授权吧！", Toast.LENGTH_SHORT).show();
            //提示之后可以继续请求权限
            ActivityCompat.requestPermissions(this, permission, PERMISSION_RESULT);
        } else {
            //没有权限，去请求权限
            ActivityCompat.requestPermissions(this, permission, PERMISSION_RESULT);
        }
    }

    /**
     * 打开相机
     */
    private void openCameraForResult() {

        //
        // 延时拍照
        //

        //创建intent ，设置action
        Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        //构建图片路径
        createImageFilePath();
        //将捕获的图片保存在imageUri
        intent.putExtra(MediaStore.EXTRA_OUTPUT, getImageUri());
        //调用相机
        startActivityForResult(intent, IMAGE_RESULT);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        switch (requestCode){
            case IMAGE_RESULT:
                //这里不能通过Intent对象去获取"data"，
                // 因为在打开相机时已经通过MediaStore.EXTRA_OUTPUT告诉相机：你把图片放在我传给你的Uri中
                //所以可以直接通过BitmapFactory在存储路径中获取图片

            /*Bitmap bitmap1 = BitmapFactory.decodeFile(mImageFilePath);
            Log.i("--bitmap1--", bitmap1.getHeight() + "<===>" + bitmap1.getWidth());
            //I/--bitmap1--: 4608<===>3456*/

           /* //1.快速加载大图，获取采样后的图片 1/8比例 对比打印：其实是宽高都缩小8倍
            BitmapFactory.Options options = new BitmapFactory.Options();
            options.inSampleSize = 8;
            Bitmap bitmap2 = BitmapFactory.decodeFile(mImageFilePath, options);
            Log.i("--bitmap2--", bitmap2.getHeight() + "<===>" + bitmap2.getWidth());
            //I/--bitmap2--: 576<===>432
            imageView.setImageBitmap(bitmap2);*/

                //2.按照具体环境配置比例，尽可能地填充显示范围：比如显示屏宽高
                //接收屏幕宽高 x==width;y==height
                Point disPlayer = new Point();
                //获取屏幕宽高
                getWindowManager().getDefaultDisplay().getSize(disPlayer);
                //创建解码图像的Options
                BitmapFactory.Options bitmapOptions = new BitmapFactory.Options();
                //inJustDecodeBounds如果设置为true，解码器会返回null，不会返回bitmap，
                // 但是BitmapFactory.Options.outxxx属性会被设置值，运行解码器去查询bitmap，不会将bitmap加载进内存。
                bitmapOptions.inJustDecodeBounds = true;
                //让解码器去查询该图片（返回bitmap为null，但是给BitmapFactory.Options.outxxx属性设置值）
                BitmapFactory.decodeFile(mImageFilePath, bitmapOptions);
                //显示屏宽高与图片宽高对比
                //屏幕高 disPlayer.y
                //屏幕宽disPlayer.x
                //图片高 bitmapOptions.outHeight
                //图片宽 bitmapOptions.outWidth
                //高之比
                int heightRatio = (int) Math.ceil(bitmapOptions.outHeight / ((float) disPlayer.y));
                //宽之比
                int widthRatio = (int) Math.ceil(bitmapOptions.outWidth / ((float) disPlayer.x));
                //解释下Math.round(),Math.ceil(),Math.floor()
                //1，Math.round()：round是附近的意思，取四舍五入
                //2，Math.ceil()：ceil是天花板的意思，取上限值
                //3，Math.floor()：floor是地板的意思，取下限值
                //比如我打印的屏幕高: 2034；图片高: 4608；比值大概是2.+，ceil之后的值就是3。
                Log.i("--屏幕高 ", disPlayer.y + "");
                Log.i("--屏幕宽 ", disPlayer.x + "");
                Log.i("--图片高 ", bitmapOptions.outHeight + "");
                Log.i("--图片宽 ", bitmapOptions.outWidth + "");
                Log.i("--高之比", heightRatio + "");
                Log.i("--宽之比", widthRatio + "");
                //I/--屏幕高: 2034
                //I/--屏幕宽: 1080
                //I/--图片高: 4608
                //I/--图片宽: 3456
                //I/--高之比: 3
                //I/--宽之比: 4
//            if (heightRatio > 1 && widthRatio > 1) {
//                //两个比例都大于1
//                //采样的比例取heightRatio和widthRatio中的最大值
//                bitmapOptions.inSampleSize = Math.max(heightRatio, widthRatio);
//
//            }
                bitmapOptions.inSampleSize = 1;  //设置为原图上传
                //设置为false取解码图片
                bitmapOptions.inJustDecodeBounds = false;
                //获取缩小之后的图片
                Log.i("--bitmapOptions", bitmapOptions+ "");
                Bitmap bitmap = BitmapFactory.decodeFile(mImageFilePath);

                Log.i("--------",mImageFilePath+"---------------------------");

                imageView.setImageBitmap(bitmap);
                Log.i("--缩小后宽：", bitmap.getWidth() + "");
                Log.i("--缩小后高：", bitmap.getHeight() + "");
                //I/--缩小后宽：: 864
                //I/--缩小后高：: 1152

                //
                // 添加一个对bitmap的操作 满足条件执行file的赋值
                //
                file= new File(mImageFilePath); //图片赋值file
                break;

            case SELECT_PIC_BY_PICK_PHOTO:
                //data中自带有返回的uri
                Uri photoUri = data.getData();
                String[] filePathColumn = { MediaStore.Images.Media.DATA };
                //获取照片路径
                try {
                    Cursor cursor = getContentResolver().query(photoUri,
                            filePathColumn, null, null, null);
                    cursor.moveToFirst();
                    int columnIndex = cursor.getColumnIndex(filePathColumn[0]);
                    picturePath = cursor.getString(columnIndex);
                    cursor.close();
                    Bitmap bitmap1 = BitmapFactory.decodeFile(picturePath);
                    imageView.setImageBitmap(bitmap1);
                    file= new File(picturePath);
                    Log.i("takephoto","************"+picturePath);
                } catch (Exception e) {
                    Log.e("Exception", e.getMessage(),e);
                }
            break;
        }
    }


    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode != PERMISSION_RESULT) {
            return;
        }

        if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            //因为我就申请一个权限，所以可以通过grantResults[0]就是我申请的权限。
            //用户同意权限，打开相机
            openCameraForResult();
        } else {
            //这里本意并不是重新请求权限，是通过方法shouldShowRequestPermissionRationale()去给用户做提示。
            requestPermission(mPermission);
        }
    }
}

package com.example.zl.menurecognitiondemo;

import java.io.Serializable;

public class ResponseResult implements Serializable {
    private boolean statuus;
    private String[] data;
    private String msg;

    public ResponseResult() {
    }

    public ResponseResult(boolean statuus, String[] data, String msg) {
        this.statuus = statuus;
        this.data = data;
        this.msg = msg;
    }

    public boolean isStatuus() {
        return statuus;
    }

    public void setStatuus(boolean statuus) {
        this.statuus = statuus;
    }

    public String[] getData() {
        return data;
    }

    public void setData(String[] data) {
        this.data = data;
    }

    public String getMsg() {
        return msg;
    }

    public void setMsg(String msg) {
        this.msg = msg;
    }
}

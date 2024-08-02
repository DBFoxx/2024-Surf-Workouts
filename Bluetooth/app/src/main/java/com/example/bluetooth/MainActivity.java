package com.example.bluetooth;


import android.annotation.SuppressLint;
import android.app.AlertDialog;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.Vibrator;
import android.text.TextUtils;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import java.util.Set;


public class MainActivity extends AppCompatActivity implements View.OnClickListener {
    private static final String TAG = "MyBluetooth";
    public String name_Smartwatch = "OPPO Watch SE 8008";
    public String name_tablet = "vivo Pad Air";
    private static final String VIBRATE_SHORT = "VIBRATE_SHORT";
    private static final String VIBRATE_LONG = "VIBRATE_LONG";
    private Vibrator vibrator;
    private Button ck_bluetooth; // 声明一个复选框对象
    private Button ck_vibrate_short;
    private Button ck_vibrate_long;
    private int count_short = 0;
    private int count_long = 0;
    private BluetoothAdapter mBluetooth; // 声明一个蓝牙适配器对象

    private BluetoothSocket mBlueSocket; // 声明一个蓝牙设备的套接字对象
    private Handler mHandler = new Handler(Looper.myLooper()); // 声明一个处理器对象
    private int mOpenCode = 1; // 是否允许扫描蓝牙设备的选择对话框返回结果代码


    @SuppressLint("MissingPermission")
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);

        vibrator = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);

        initBluetooth();
        ck_bluetooth = findViewById(R.id.ck_bluetooth);
        ck_vibrate_short = findViewById(R.id.ck_vibrate_short);
        ck_vibrate_long = findViewById(R.id.ck_vibrate_long);

        ck_bluetooth.setOnClickListener(this);
        ck_vibrate_short.setOnClickListener(this);
        ck_vibrate_long.setOnClickListener(this);
    }

    private void initBluetooth() {
        // 获取系统默认的蓝牙适配器
        mBluetooth = BluetoothAdapter.getDefaultAdapter();

        if (mBluetooth == null) {
            Toast.makeText(this, "该设备不支持蓝牙", Toast.LENGTH_SHORT).show();
            finish(); // 关闭当前页面
        }
        if (!mBluetooth.isEnabled()) {
            Toast.makeText(this, "请开启蓝牙", Toast.LENGTH_SHORT).show();
            finish(); // 关闭当前页面
        }
    }

    private Runnable mDiscoverable = new Runnable() {
        public void run() {
            // Android8.0要在已打开蓝牙功能时才会弹出下面的选择窗
            if (BluetoothUtil.getBlueToothStatus()) { // 已经打开蓝牙
                // 弹出是否允许扫描蓝牙设备的选择对话框
                Intent intent = new Intent(BluetoothAdapter.ACTION_REQUEST_DISCOVERABLE);
                startActivityForResult(intent, mOpenCode);
            } else {
                mHandler.postDelayed(this, 1000);
            }
        }
    };

    // 定义一个连接侦听任务
    //创建并启动了一个 BlueAcceptTask 对象，用于处理蓝牙连接。
    //当成功连接后，会执行传递的 lambda 表达式，即调用 startReceiveTask(socket) 方法来处理接收到的 BluetoothSocket。
    private Runnable mAccept = new Runnable() {
        @Override
        public void run() {
            if (mBluetooth.getState() == BluetoothAdapter.STATE_ON) { // 已连接
                // 创建一个蓝牙设备侦听线程，成功侦听就启动蓝牙消息的接收任务
                BlueAcceptTask acceptTask = new BlueAcceptTask(
                        MainActivity.this, true, socket -> startReceiveTask(socket));
                acceptTask.start();
            } else { // 未连接
                // 延迟1秒后重新启动连接侦听任务
                mHandler.postDelayed(this, 1000);
            }
        }
    };



    public void onClick(View v) {
        if (v.getId() == R.id.ck_bluetooth) {
            if (!BluetoothUtil.getBlueToothStatus()) { // 还未打开蓝牙
                BluetoothUtil.setBlueToothStatus(true); // 开启蓝牙功能
            }
            mHandler.post(mDiscoverable);
            mHandler.postDelayed(mAccept, 1000); // 服务端需要，客户端不需要
            Set<BluetoothDevice> pairedDevices = mBluetooth.getBondedDevices();
            if (pairedDevices.size() > 0) {
                for (BluetoothDevice device : pairedDevices) {
                    Log.d(TAG, "Paired device: " + device.getName() + " - " + device.getAddress());
                    if (device.getName().equals(name_Smartwatch)) {
                        BlueConnectTask connectTask = new BlueConnectTask(this, device, socket -> startReceiveTask(socket));
                        connectTask.start();
                        ck_bluetooth.setText("蓝牙已连接手表");
                    }
                    if (device.getName().equals(name_tablet)) {
                        BlueConnectTask connectTask = new BlueConnectTask(this, device, socket -> startReceiveTask(socket));
                        connectTask.start();
                        ck_bluetooth.setText("蓝牙已连接平板电脑");
                    }
                }
            } else {
                ck_bluetooth.setText("已配对设备为0");
            }
        }
        if (v.getId() == R.id.ck_vibrate_short){
            count_short++;
            BluetoothUtil.writeOutputStream(mBlueSocket, VIBRATE_SHORT);
            ck_vibrate_short.setText("短振的指令已发送" + count_short + "次");
        }else if (v.getId() == R.id.ck_vibrate_long){
            count_long++;
            BluetoothUtil.writeOutputStream(mBlueSocket, VIBRATE_LONG);
            ck_vibrate_long.setText("长振的指令已发送" + count_long + "次");
        }
    }



    // 启动蓝牙消息的接收任务
    private void startReceiveTask(BluetoothSocket socket) {
        if (socket == null) {
            return;
        }
        mBlueSocket = socket;
        // 创建一个蓝牙消息的接收线程
        BlueReceiveTask receiveTask = new BlueReceiveTask(this, mBlueSocket, message -> {
            if (!TextUtils.isEmpty(message)) {
                String command = null;

                if (vibrator != null && vibrator.hasVibrator()) {
                    // 使设备振动 500 毫秒
                    if (message.equals(VIBRATE_SHORT)) {
                        vibrator.vibrate(500);
                        command = "短振500毫秒";
                    }
                    if (message.equals(VIBRATE_LONG)) {
                        vibrator.vibrate(1000);
                        command = "长振1000毫秒";
                    }
                    // 弹出收到消息的提醒对话框
                    AlertDialog.Builder builder = new AlertDialog.Builder(this);
                    builder.setTitle("收到指令：").setMessage(command);
                    builder.setPositiveButton("确定", null);
                    builder.create().show();
                } else if (!vibrator.hasVibrator()) {
                    // 弹出收到消息的提醒对话框
                    AlertDialog.Builder builder = new AlertDialog.Builder(this);
                    builder.setTitle("结束").setMessage("收到指令，但因设备没有振动器，所以未执行指令");
                    builder.setPositiveButton("确定", null);
                    builder.create().show();
                }

            }
        });
        receiveTask.start();
    }

    protected void onDestroy() {
        super.onDestroy();
        if (mBlueSocket != null) {
            try {
                mBlueSocket.close(); // 关闭蓝牙设备的套接字
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
}




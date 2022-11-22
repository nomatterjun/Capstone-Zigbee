package com.example.myapplication;

import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.android.volley.toolbox.JsonArrayRequest;

import com.android.volley.AuthFailureError;
import com.android.volley.Request;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.Volley;

import org.eazegraph.lib.charts.BarChart;
import org.eazegraph.lib.models.BarModel;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

public class MainActivity extends AppCompatActivity  {
    BarChart barChart;
    Button button;
    RecyclerView recyclerView;
    RecyclerAdapter adapter = new RecyclerAdapter();
    ArrayList<Data> list = new ArrayList<>();
    ArrayList<String> state_cnt = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        barChart = (BarChart) findViewById(R.id.barchart);
        button = (Button) findViewById(R.id.send_btn);
        recyclerView = findViewById(R.id.recyclerview);
        //RecyclerView
        LinearLayoutManager linearLayoutManager = new LinearLayoutManager(this);

        recyclerView.setLayoutManager(linearLayoutManager);
        //RecyclerView에 어댑터 적용
        recyclerView.setAdapter(adapter);

        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                sendRequest();
            }
        });

        if(AppHelper.requestQueue != null) {
            AppHelper.requestQueue = Volley.newRequestQueue(getApplicationContext());
        } //RequestQueue 생성


        }




    public void sendRequest() {
//        String url = "http://10.93.84.21:8123/api/history/period?filter_entity_id=sun.sun";
        String url = "https://9aabc7a3-c108-4330-8ec1-0b315e4f4045.mock.pstmn.io/haeji";

        JsonArrayRequest jsonArrayRequest = new JsonArrayRequest(
                Request.Method.GET,
                url,
                null,
                new Response.Listener<JSONArray>() {

                    public void onResponse(JSONArray response) {
                        try {
//                            이중 배열 JSON 데이터 parsing
                            for (int i = 0; i < response.length(); i++) {
                                JSONArray internal_array = response.getJSONArray(i);
                                for(int k=0; k < internal_array.length(); k++) {
                                    JSONObject object = internal_array.getJSONObject(k);
                                    list.add(new Data(
                                            object.getString("entity_id"),
                                            object.getString("state"),
                                            object.getString("last_changed"),
                                            object.getString("last_updated") ));

//                                    String get_status = object.getString("status");

                                    // 각 상태 횟수 구하기
                                    state_cnt.add(object.getString("state"));

                                }
                            }

                        } catch (JSONException e) {
                            e.printStackTrace();
                        }

                        // 리사이클러 뷰 어댑터 적용
                        adapter.setattList(list);

                        // 그래프 y축 값 구하기
                        int Meal_cnt = Collections.frequency(state_cnt,"Meal");
                        int Work_cnt = Collections.frequency(state_cnt,"Work");
                        int Media_cnt = Collections.frequency(state_cnt,"Media");
                        int Sleep_cnt = Collections.frequency(state_cnt,"Sleep");

                        // 그래프 출력
                        barChart.clearChart();

                        barChart.addBar(new BarModel("Meal",Meal_cnt, 0xFF56B7F1));
                        barChart.addBar(new BarModel("Work", Work_cnt, 0xFF56B7F1));
                        barChart.addBar(new BarModel("Media", Media_cnt, 0xFF56B7F1));
                        barChart.addBar(new BarModel("Sleep", Sleep_cnt, 0xFF56B7F1));

                        barChart.startAnimation();


                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
//                println("에러 ->" + error.getMessage());
                error.printStackTrace();
            }
        })

        {
//            @Override
//            protected Map<String, String> getParams() throws AuthFailureError {
//                Map<String,String> params = new HashMap<String,String>();
//                return params;
//            }

//            @Override
//            public Map<String, String> getHeaders() {
//                Map<String, String> params = new HashMap<String, String>();
//                params.put("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIyNjA1ODZmMjg3YjM0M2JkYmFiN2Y4MmU3OGNjNmZiNyIsImlhdCI6MTY2NzgxMDg4OCwiZXhwIjoxOTgzMTcwODg4fQ.FjiV4F21eEgsF733vK1uSai9CX4ciA76K92y7RMnpvs");
//                params.put("content-type", "application/json");
//                return params;
//            }
        };





        jsonArrayRequest.setShouldCache(false); //이전 결과 있어도 새로 요청하여 응답을 보여준다.
        AppHelper.requestQueue = Volley.newRequestQueue(this); // requestQueue 초기화 필수
        AppHelper.requestQueue.add(jsonArrayRequest);

//        println("요청 보냄.");
    }






//    public void println(String data) {
//        textView.setText(data +"\n");
//    }
}
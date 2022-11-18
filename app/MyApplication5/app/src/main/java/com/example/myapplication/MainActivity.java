package com.example.myapplication;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import com.android.volley.toolbox.JsonArrayRequest;
import com.jjoe64.graphview.GraphView;
import com.jjoe64.graphview.series.DataPoint;
import com.jjoe64.graphview.series.LineGraphSeries;

import com.android.volley.AuthFailureError;
import com.android.volley.Request;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.Volley;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;



import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;



public class MainActivity extends AppCompatActivity  {
    TextView textView;
    Button button;
    GraphView graphView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        graphView = findViewById(R.id.idGraphView);

        // on below line we are adding data to our graph view.
        LineGraphSeries<DataPoint> series = new LineGraphSeries<DataPoint>(new DataPoint[]{
                // on below line we are adding
                // each point on our x and y axis.
                new DataPoint(1, 2),
                new DataPoint(1, 3),
                new DataPoint(2, 4),
                new DataPoint(3, 9),
                new DataPoint(4, 6),
                new DataPoint(5, 3),
                new DataPoint(6, 6),
                new DataPoint(7, 1),
                new DataPoint(8, 2)
        });

        // after adding data to our line graph series.
        // on below line we are setting
        // title for our graph view.
        graphView.setTitle("My Graph View");

        // on below line we are setting
        // text color to our graph view.
        graphView.setBackgroundColor(getResources().getColor(R.color.white));
        graphView.setTitleColor(R.color.purple_200);

        // on below line we are setting
        // our title text size.
        graphView.setTitleTextSize(18);

        // on below line we are adding
        // data series to our graph view.
        graphView.addSeries(series);

        textView = (TextView) findViewById(R.id.textView);


        button = (Button) findViewById(R.id.send_btn);
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
        String url = "http://10.93.84.21:8123/api/history/period?filter_entity_id=sun.sun";
        //String url = "https://9aabc7a3-c108-4330-8ec1-0b315e4f4045.mock.pstmn.io/haeji";

        JsonArrayRequest jsonArrayRequest = new JsonArrayRequest(
                Request.Method.GET,
                url,
                null,
                new Response.Listener<JSONArray>() {

                    public void onResponse(JSONArray response) {
                        try {
//                            이중 배열 JSON 데이터 parsing
                            List<String> last_state = new ArrayList<String>();
                            for (int i = 0; i < response.length(); i++) {
                                JSONArray internal_array = response.getJSONArray(i);
                                for(int k=0; k < internal_array.length(); k++) {
                                    JSONObject object = internal_array.getJSONObject(k);
                                    String entity_id = object.getString("entity_id");
                                    String state = object.getString("state");
                                    String last_changed = object.getString("last_changed");
                                    String last_updated = object.getString("last_updated");

//                                    last_state.add(object.getString("state"));

                                    textView.append(entity_id + ", " + state + ", " +last_changed +", " + last_updated);
//                                    textView.setText(last_changed +", " + last_updated);
                                }

                            }
//                            state의 마지막 값(현재 상황 출력)
//                            String last = last_state.get(last_state.size() - 1);
//                            textView.setText(last);
//                            textView.setText(last);

                        } catch (JSONException e) {
                            e.printStackTrace();
                        }
                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                println("에러 ->" + error.getMessage());
                error.printStackTrace();
            }
        })
        {
            @Override
            protected Map<String, String> getParams() throws AuthFailureError {
                Map<String,String> params = new HashMap<String,String>();
                return params;
            }

            @Override
            public Map<String, String> getHeaders() {
                Map<String, String> params = new HashMap<String, String>();
                params.put("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIyNjA1ODZmMjg3YjM0M2JkYmFiN2Y4MmU3OGNjNmZiNyIsImlhdCI6MTY2NzgxMDg4OCwiZXhwIjoxOTgzMTcwODg4fQ.FjiV4F21eEgsF733vK1uSai9CX4ciA76K92y7RMnpvs");
                params.put("content-type", "application/json");
                return params;
            }
        };

        jsonArrayRequest.setShouldCache(false); //이전 결과 있어도 새로 요청하여 응답을 보여준다.
        AppHelper.requestQueue = Volley.newRequestQueue(this); // requestQueue 초기화 필수
        AppHelper.requestQueue.add(jsonArrayRequest);

        println("요청 보냄.");
    }

    public void println(String data) {
        textView.setText(data +"\n");
    }
}
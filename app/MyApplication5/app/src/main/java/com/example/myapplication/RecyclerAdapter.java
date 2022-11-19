package com.example.myapplication;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.ArrayList;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

public class RecyclerAdapter extends RecyclerView.Adapter<RecyclerAdapter.ViewHolder> {

    private ArrayList<Data> mData = new ArrayList<>();

    // 아이템 뷰를 저장하는 viewholder 클래스
    public class ViewHolder extends RecyclerView.ViewHolder {

        TextView state_list;
        TextView id_list;
        TextView changed_list;
        TextView updated_list;

        public ViewHolder(@NonNull View itemView) {
            super(itemView);

            state_list = itemView.findViewById(R.id.state_list);
            id_list = itemView.findViewById(R.id.id_list);
            changed_list = itemView.findViewById(R.id.changed_list);
            updated_list = itemView.findViewById(R.id.updated_list);

        }

        void onBind(Data data1) {
            state_list.setText(data1.getState());
            id_list.setText(data1.getEntity_id());
            changed_list.setText(data1.getLast_changed());
            updated_list.setText(data1.getLast_updated());
        }
    }

    // 아이템 뷰를 위한 뷰홀더 객체를 생성하여 return
    @NonNull
    @Override
    public RecyclerAdapter.ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        Context context = parent.getContext();
        LayoutInflater inflater = (LayoutInflater) context.getSystemService(Context.LAYOUT_INFLATER_SERVICE);

        View view = inflater.inflate(R.layout.rowitem, parent, false);
        RecyclerAdapter.ViewHolder viewHolder = new RecyclerAdapter.ViewHolder(view);

        return viewHolder;
    }

    @Override
    public void onBindViewHolder(@NonNull RecyclerAdapter.ViewHolder holder, int position) {
        holder.onBind(mData.get(position));
    }

    // 사이즈
    @Override
    public int getItemCount() {
        return mData.size();
    }


    // data 모델의 객체들을 list에 저장
    public void setattList(ArrayList<Data> list) {
        this.mData = list;
        notifyDataSetChanged();
    }

}
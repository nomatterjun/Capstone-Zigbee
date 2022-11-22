package com.example.myapplication;

public class Data {
    private String state;
//    private String entity_id;
//    private String last_changed;
//    private String last_updated;

    public String getState() {return state;}
    public void setState(String state) {this.state = state;}

//    public String getEntity_id() {return entity_id;}
//    public void setEntity_id(String entity_id) {this.entity_id = entity_id;}

//    public String getLast_changed() {return last_changed;}
//    public void setLast_changed(String last_changed) {this.last_changed = last_changed;}
//
//    public String getLast_updated() {return last_updated;}
//    public void setLast_updated(String last_changed) {this.last_updated = last_updated;}

    public Data(String state) {
        this.state = state;
//        this.entity_id = entity_id;
//        this.last_changed = last_changed;
//        this.last_updated = last_updated;
    }

    public Data () {
        this.state = state;

    }

}
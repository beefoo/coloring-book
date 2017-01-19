import processing.pdf.*;
// import processing.dxf.*;

// data
String data_file = "data/nuisance.json";
int padding = 40;
boolean export = true;

StringList stations = new StringList("8534720", "8665530", "8575512", "8658120");
StationList stationList;

void setup() {
  size(1280, 1656, P3D);
  colorMode(RGB, 255, 255, 255, 100);
  //smooth(8);
  //noStroke();
  //noFill();
  background(255);

  // get speech data
  JSONObject data_json = loadJSONObject(data_file);
  stationList = new StationList(stations, data_json);

  noLoop();
}

void draw(){
  if (export) {
    beginRaw(PDF, "data/nuisance.pdf");
    // beginRaw(DXF, "data/nuisance.dxf");
  }
  //stationList.renderSLR(padding, padding, width - padding * 2, 0.5 * (height - padding * 2));
  
  //pushMatrix();
  //background(255);
  //translate(200, 300, 0);
  //stroke(0);
  //strokeWeight(2);
  //fill(255);
  //hint(ENABLE_DEPTH_TEST);
  //hint(ENABLE_DEPTH_SORT);
  //box(200, 300, 200);
  //popMatrix();
  
  hint(ENABLE_DEPTH_TEST);
  //hint(ENABLE_DEPTH_SORT);
  beginShape();
  stroke(0);
  strokeWeight(2);
  fill(255);
  vertex(100, 100, 100);
  vertex(200, 100, 100);
  vertex(200, 200, 100);
  vertex(100, 200, 100);
  vertex(100, 100, 100);
  endShape();
  
  beginShape();
  stroke(0);
  strokeWeight(2);
  fill(255);
  vertex(150, 150, 200);
  vertex(250, 150, 200);
  vertex(250, 250, 200);
  vertex(150, 250, 200);
  vertex(150, 150, 200);
  endShape();
  
  if (export) {
    endRaw(); 
  }
}

void mousePressed() {
  exit();
}

class StationList
{
  int stationDepth = 30;
  int stationMargin = 10;

  ArrayList<Station> stations;

  StationList(StringList stationIds, JSONObject d) {
    stations = new ArrayList<Station>();
    JSONObject stationsData = d.getJSONObject("stationData");
    for (String stationId : stationIds) {
      JSONObject stationData = stationsData.getJSONObject(stationId);
      stations.add(new Station(stationData, d.getJSONArray("slrRange"), d.getJSONArray("inundationRange")));
    }
  }

  ArrayList<Station> getStations(){
    return stations;
  }

  void renderInundation(float x, float y, float w, float h){
    float z = 0;
    for (Station station : stations) {
      station.renderInundation(x, y, z, w, h, stationDepth);
      z = z - stationDepth - stationMargin;
    }
  }

  void renderSLR(float x, float y, float w, float h){
    float z = 0;
    for (Station station : stations) {
      station.renderInundation(x, y, z, w, h, stationDepth);
      z = z - stationDepth - stationMargin;
    }
  }
}

class Station
{
  String label;
  JSONArray slrData;
  JSONArray inundationData;

  Station(JSONObject d, JSONArray slrRange, JSONArray inundationRange) {
    label = d.getString("label");
    slrData = d.getJSONArray("slrData");
    inundationData = d.getJSONArray("inundationData");

    // process slr data
    for (int i = 0; i < slrData.size(); i++) {
      float value = slrData.getJSONObject(i).getFloat("value");
      slrData.getJSONObject(i).setFloat("valueNorm", norm(value, slrRange.getFloat(0), slrRange.getFloat(1)));
    }

    // process inundation data
    for (int i = 0; i < inundationData.size(); i++) {
      float value = inundationData.getJSONObject(i).getFloat("value");
      inundationData.getJSONObject(i).setFloat("valueNorm", norm(value, inundationRange.getFloat(0), inundationRange.getFloat(1)));
    }
  }

  void render(JSONArray data, float x0, float y0, float z0, float cw, float ch, float depth){
    float z = z0;
    float w = 1.0 * cw / data.size();

    for (int i = 0; i < data.size(); i++) {
      JSONObject d = data.getJSONObject(i);
      float x = x0 + w * i;
      float h = d.getFloat("valueNorm") * ch;
      float y = -1.0 * h - y0;

      pushMatrix();
      smooth();
      translate(x, y, z);
      fill(255);
      stroke(0);
      box(w, h, depth);
      popMatrix();
    }
  }

  void renderInundation(float x0, float y0, float z0, float cw, float ch, float d) {
    render(inundationData, x0, y0, z0, cw, ch, d);
  }

  void renderSLR(float x0, float y0, float z0, float cw, float ch, float d) {
    render(slrData, x0, y0, z0, cw, ch, d);
  }
}
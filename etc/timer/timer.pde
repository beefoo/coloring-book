String outputFrameFile = "output/frames/frames-####.png";
boolean captureFrames = true;

int fps = 24;
float frameMs = (1.0/fps) * 1000;

int startTime = 0;
int startMs = 60000;
float elapsedMs = 0;


void setup(){
  size(1920, 1080);
  colorMode(RGB, 255, 255, 255, 100);
  frameRate(fps);
  smooth();
  noStroke();
  
  PFont font = createFont("OpenSans-Regular", 200, true);
  textAlign(LEFT, BOTTOM);
  textFont(font);

}
void draw(){
  background(#000000);
  fill(#ffffff);
  
  elapsedMs += frameMs;
  float displayMs = startMs - elapsedMs;
  int display = int(displayMs) / 1000;
  
  if (display < 0) {
    exit();
    
  } else {
    text(":"+nf(display, 2), 40, height-40);
    
    if(captureFrames) {
      saveFrame(outputFrameFile);
    }
  }
}
Required Environment
Python 3.6
Pillow (PIL Fork) 5.1.x

Installation of PIL:
 $ pip install Pillow
Make sure the 'null.jpeg' file is in the current running directory.

Project files
aerial_image.py
null.jpeg

Run Instructions
Simply open a Terminal at the project directory, run, for example:

# Example for IIT Campus
python main.py 41.839341 -87.629504 41.831092 -87.623239
or

# Example for Bean/Cloud Gate
$ python main.py 41.882981 -87.623496 41.882397 -87.623076

The output desired image is then saved as 'result.jpg', one at a time.

Note: The four parameters represents lat1, lon1, lat2, lon2, respectively.
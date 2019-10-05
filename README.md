This is a WIP project aiming to reverse engineer the Medieval/Space Engineers .mwm model filetype to enable reading/writing binary data in python.

The project contains classes for reading and writing most data types found in the .mwm file, but the interface for processing files is currently not easily usable.

The structure of an .mwm file is quite basic in that it contains just a header addressing the location of each part of the model data, followed by all the data.

  * **Header**: The header contains a dictionary of "tags". Each dictionary entry is made of a string† for the key, followed by the a 4 byte memory address (little-endian) of the corresponding tag data.
  * **Body**: The body contains the data for each tag. The different tags contain different data and must be processed accordingly.
  
  _† Most (all?) strings in the file are preceeded by a single byte indicating the length of the string about to be read._


The file may contain an inline Havok .hkt file for collision data under the HavokCollisionGeometry tag.
The Havok tagfile can not currently be read due to the proprietary filetype but I have had partial success reverse engineering it.
You can find an 010 Editor binary template file here https://gist.github.com/adamb70/070730496ba23d0ea109eb926fdc3887.
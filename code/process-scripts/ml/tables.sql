create table repet (                   
   id integer primary key autoincrement,
   window_size int,
   window_type varchar(256),
   period integer,
   bg_sdr real,
   fg_sdr real,
   fg_file varchar(256),
   bg_file varchar(256),
   period_min integer,
   period_max integer,
   suggested_period integer,
   default_fg_sdr integer,
   default_bg_sdr integer);


create table nearest_neighbor (                   
   id integer primary key autoincrement,
   window_size int,
   window_type varchar(256),
   period integer,
   standard_deviation real,
   bpm real, 
   fg_file varchar(256),
   bg_file varchar(256),
   period_min integer,
   period_max integer,
   suggested_period integer);
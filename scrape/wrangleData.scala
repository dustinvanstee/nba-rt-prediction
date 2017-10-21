//my scala code guess ...
//:load /data/work/programming/scala/ticket.scala

import scala.io
val source = scala.io.Source.fromFile("/data/work/hh/2016_03_marchmadness/nbadata/nba.rts.all")

val filein:Iterator[String] = source.getLines //.mkString("\n")


var ptokenmap :Map[String ,String] = Map("test" -> "test")
var lineno = 1
// so since there are many games running simultaneously, I need to make a map of date.teama.teamb => Array[string]


for (line <- filein) {
  val tokens = line.split(',')

  val gameid = tokens(0)+tokens(2)+tokens(4)

  if(tokens.length != 8 && tokens.length !=9) {
    println("Line number " + lineno + " : 8 fields not detected")
    exit
  }

  if(tokens(0).length != 10) {
    println("Line number " + lineno + " : malformed date field")
    exit
  }
  if(tokens(1).length != 8) {
    println("Line number " + lineno + " : malformed time field")
    exit
  }
  // This is case when i started adding espn gameid
  if(tokens.length == 9) {
    if(tokens(8).length != 9){
      println("Line number " + lineno + " : malformed gameid field")
      exit
    }
  }



  // Simple array == doesnt work because it comparing the reference i thinks
  if(ptokenmap contains gameid) {



    if(tokens.slice(2,7).sameElements(ptokenmap(gameid).split(',').slice(2,7))) {
      //println("dup = " + tokens.mkString)
    } else {
      //println("uniq = " + tokens.mkString)
      println(line)
      ptokenmap = ptokenmap + (gameid->line)
    }
    //println(tokens(0))
  } else {
    // add
    ptokenmap = ptokenmap + (gameid->line)
  }


  lineno += 1
}


// snrpl
// \(END OF 3RD\),12.0\n
// \(END OF 1ST\),36.0\n


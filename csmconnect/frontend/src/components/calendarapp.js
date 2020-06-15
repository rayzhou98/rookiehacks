import React, { Component } from "react";
import { render } from "react-dom";
import { BrowserRouter, Redirect } from "react-router-dom";

class CalendarEvent extends Component {
   constructor(props) {
      super(props);
      var date = props.date;
      var width = 200;
      var col = props.days.indexOf(date);
      col = col + 2;
      var parsedStartTime = this.parseTime(props.start_time);
      var startHour = parsedStartTime[0];
      var startMinute = parsedStartTime[1];
      var startRow = startHour - 5;

      var parsedEndTime = this.parseTime(props.end_time);
      var endHour = parsedEndTime[0];
      var endMinute = parsedEndTime[1];
      var span = endHour - startHour + 1;

      var position = "absolute";
      var top = (startMinute/60) * 50;
      var bottom = 50 - ((endMinute/60) * 50);
      var zIndex = 0;
      this.state = {
          styles: {
            gridColumn: col,
            width: width,
            gridRow: startRow.toString() +  "/ span " + span.toString(),
            position: position,
            top: top,
            bottom: bottom,
            zIndex: zIndex,
            backgroundColor: "#7167B9",
            textDecoration: "none",
            color: "#E5E5E5"
          }
      }
 }

   parseTime(time) {
     var time = time.split(":");
     var minuteSuffix = time[1].split(" ");
     var hour = parseInt(time[0], 10);
     if (minuteSuffix[1] === "PM") {
       hour = hour + 12;
     }
     var minute = parseInt(minuteSuffix[0], 10);
     return [hour, minute];
   }

   render() {
    if (this.props.inRange) {
      if (this.props.is_mentor === 'true') {
        var url = "meetingdetails/" + this.props.id;
        if (this.props.student) {
          return (<a className="event" style={this.state.styles} href={url}>
                  <div> {this.props.start_time}
                  <br></br>
                  Meeting with {this.props.student.student_name}
                  </div>
               </a>);
        }
        else {
          return (<a className="event" style={this.state.styles} href={url}>
              <div> {this.props.start_time}
              <br></br>
              No student assigned.
              </div>
              </a>
            );
        }
      }
      else {
        var url;
        if (this.props.dashboard === 'true') {
          url = "meetingdetails/" + this.props.id;
        }
        else {
          url = "joinmeeting/" + this.props.id;
        }
        return (<a className="event" style={this.state.styles} href={url}>
                  <div> {this.props.start_time}
                  <br></br>
                  Meeting with {this.props.mentor.mentor_name}
                  </div>
               </a>);
      }
     }
     else {
       return null;
     }
    }

  componentDidUpdate(prevProps) {
    if (this.props.inRange !== prevProps.inRange) {
      this.setState({
          styles: {
            gridColumn: this.props.days.indexOf(this.props.date) + 2,
            width: this.state.styles.width,
            gridRow: this.state.styles.gridRow,
            position: this.state.styles.position,
            top:  this.state.styles.top,
            bottom:  this.state.styles.bottom,
            zIndex:  this.state.styles.zIndex,
            backgroundColor:  this.state.styles.backgroundColor,
            textDecoration: this.state.styles.textDecoration,
            color: this.state.styles.color
          }
      });
    }
  }
}

class Calendar extends Component {
  constructor(props) {
    super(props)
    var days = [];
    var options = { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric'};
    var firstDay;
    for (var i = 0; i < 7; i++) {
      var day = new Date();
      if (i == 0) {
        firstDay = day;
      }
      day.setDate(day.getDate() + i);
      days.push(new Intl.DateTimeFormat('en-US', options).format(day));
    }

    var times = [];
    var hour = 7;
    for (var j = 0; j < 13; j++) {
      var hour = (7 + j);
      var suffix;
      if (hour < 12) {
         suffix = "AM";
      }
      else {
        if (12 < hour) {
          hour = hour % 12;
        }
        suffix = "PM";
      }
      var timeStr = hour.toString() + " " + suffix;
      times.push(timeStr);
    }

    this.state = {
      meetings: JSON.parse(document.currentScript.getAttribute('meetings')),
      is_mentor: document.currentScript.getAttribute('is_mentor'),
      dashboard: document.currentScript.getAttribute('dashboard'),
      days: days,
      times: times,
      firstDay: firstDay
    }
  }

  renderEvent(event) {
    return <CalendarEvent date={event.date}
            start_time={event.start_time}
            end_time={event.end_time}
            location={event.location}
            description={event.description}
            student={event.student}
            mentor={event.mentor}
            days={this.state.days}
            id={event.id}
            is_mentor={this.state.is_mentor}
            dashboard={this.state.dashboard}
            inRange={this.state.days.indexOf(event.date) !== -1}
          />;
  }

  loadEvents() {
    var events = [];
    for (var i = 0; i < this.state.meetings.length; i++) {
       events.push(this.renderEvent(this.state.meetings[i]));
    }
    return events;
  }

  changeDates(isNext) {
    var days = [];
    var options = { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric'};
    var firstDay;
    if (isNext) {
      for (var i = 1; i < 8; i++) {
        var day = new Date();
        day.setDate(this.state.firstDay.getDate() + 6 + i);
        if (i == 1) {
          firstDay = day;
        }
        days.push(new Intl.DateTimeFormat('en-US', options).format(day));
      }
    }
    else {
      for (var i = 7; i > 0; i--) {
        var day = new Date();
        day.setDate(this.state.firstDay.getDate() - i);
        if (i == 7) {
          firstDay = day;
        }
        days.push(new Intl.DateTimeFormat('en-US', options).format(day));
      }
    }
    this.setState({
      days: days,
      firstDay: firstDay
    });
  }

   render() {
     return (
       <div className="outer-container">
         <div className="nav-container">
            <div className="button" onClick={() => this.changeDates(false)}>Prev</div>
            <div className="button" onClick={() => this.changeDates(true)}>Next</div>
         </div>
          <div className="grid-container">
            {this.loadEvents()}
            <div className="day-of-week"> </div>
            <div className="day-of-week"> {this.state.days[0]} </div>
            <div className="day-of-week"> {this.state.days[1]} </div>
            <div className="day-of-week"> {this.state.days[2]} </div>
            <div className="day-of-week"> {this.state.days[3]}</div>
            <div className="day-of-week"> {this.state.days[4]} </div>
            <div className="day-of-week"> {this.state.days[5]} </div>
            <div className="day-of-week"> {this.state.days[6]} </div>
            <div className="time"> {this.state.times[0]} </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="time"> {this.state.times[1]} </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="time"> {this.state.times[2]} </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="time"> {this.state.times[3]} </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="time"> {this.state.times[4]} </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="time"> {this.state.times[5]} </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="time"> {this.state.times[6]} </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="time"> {this.state.times[7]} </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="time"> {this.state.times[8]} </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="time"> {this.state.times[9]} </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="time"> {this.state.times[10]} </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="time"> {this.state.times[11]} </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="time"> {this.state.times[12]} </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
            <div className="grid-element"> </div>
          </div>
      </div>
     );
   }
}

export default Calendar;
const container = document.getElementById("calendar");
render(<Calendar />, container);

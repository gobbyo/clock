# Kinetic Display

The wiki contains all the documentation to get started.

Video of the display is located here: https://youtu.be/vFLpjOTYWNc

You can also view the link to the local version of the [Kinetic Display Video](media/bluekineticdisplay.mp4)

The display is a digital clock, date, indoor and outdoor temperature and humidity display. It has a white face and numbers that light when extended. The numbers are made up of segments that extend or retract to display time, date, temperature, and humidity. The display has four digits numbered 0 through 3 with a colon between digit 1 and 2. The colon is made up of two segments, an upper and a lower, which are retracted or extended for time, date, indoor or outdoor temperature and humidity.

![displayelements]

## Rotating Displays

When configured and running the display rotates time, date, temperature, and humidity each minute.

### Time
The first and last display each minute is time (12 or 24 hour).

![illustration-time]

**Time is displayed for 30 seconds** each minute from 0 to 15 seconds and from 45 to 60 seconds.

Time displays when the upper and lower colons are EXTENDED. The example shows the time as 12:43 pm when in 24-hour mode, 12:43 AM or PM when in 12-hour mode.  The switch for 12- or 24-hour time is located on the back behind digit 3.

### Month and Day

The second display each minute is the month and day.  Month is displayed on the left face of the display and the day is on the right face.

![illustration-date]

**Displays for 10 seconds** each minute from 15 to 25 seconds.

Displays when the upper and lower colons are RETRACTED. The example shows the date as December 13, where the month is the left two digits (MM) and the day is the second two digits (DD).  Note the clock face does not have enough digits to include the year along with the month and day.

### Temperature

Indoor and outdoor temperature is the third display each minute.  Indoor and outdoor temperature rotate every two minutes where the first minute is the indoor temperature and the following minute is the outdoor temperature.

![illustration-temp]

**Displays for 10 seconds** from 25 to 35 seconds.

The INTERIOR temperature displays when the UPPER colon is extended and the lower retracted.  The EXTERIOR temperature displays when the LOWER colon is extended and the upper retracted.  This example shows the INTERIOR temperature as 72° Fahrenheit. Note you can change from Fahrenheit to Celsius using the Admin page.

### Humidity

Indoor and outdoor humidity is the fourth display each minute.  Indoor and outdoor humidity rotate every two minutes where the first minute is the indoor humidity and the following minute is the outdoor humidity.

![illustration-humid]

**Displays for 10 seconds** from 35 to 45 seconds.

Like temperature, the INTERIOR humidity displays when the UPPER colon is extended and the lower retracted.  The EXTERIOR humidity displays when the LOWER colon is extended and the upper retracted.  This example shows the OUTDOOR humidity as 93%.
<!-- images -->
[displayelements]: https://raw.githubusercontent.com/wiki/gobbyo/clock/media/illustration-display-elements.png
[displayback]: media/illustration-back.png
[illustration-time]: https://raw.githubusercontent.com/wiki/gobbyo/clock/media/illustration-time.png
[illustration-date]: https://raw.githubusercontent.com/wiki/gobbyo/clock/media/illustration-date.png
[illustration-temp]: https://raw.githubusercontent.com/wiki/gobbyo/clock/media/illustration-temp.png
[illustration-humid]: https://raw.githubusercontent.com/wiki/gobbyo/clock/media/illustration-humid.png
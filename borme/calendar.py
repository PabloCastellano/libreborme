from django.core.urlresolvers import reverse
from .models import Borme
from calendar import *
from calendar import Calendar, January

import datetime
import sys


# from calendar import HTMLCalendar
class HTMLCalendar(Calendar):
    """
    This calendar returns complete HTML pages.
    """

    # CSS classes for the day <td>s
    cssclasses = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    def formatday(self, day, weekday):
        """
        Return a day as a table cell.
        """
        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        else:
            return '<td class="%s">%d</td>' % (self.cssclasses[weekday], day)

    def formatweek(self, theweek):
        """
        Return a complete week as a table row.
        """
        s = ''.join(self.formatday(d, wd) for (d, wd) in theweek)
        return '<tr>%s</tr>' % s

    def formatweekday(self, day):
        """
        Return a weekday name as a table header.
        """
        return '<th class="%s">%s</th>' % (self.cssclasses[day], day_abbr[day])

    def formatweekheader(self):
        """
        Return a header for a week as a table row.
        """
        s = ''.join(self.formatweekday(i) for i in self.iterweekdays())
        return '<tr>%s</tr>' % s

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Return a month name as a table row.
        """
        if withyear:
            s = '%s %s' % (month_name[themonth], theyear)
        else:
            s = '%s' % month_name[themonth]
        return '<caption>%s</caption>' % s

    def formatmonth(self, theyear, themonth, withyear=True):
        """
        Return a formatted month as a table.
        """
        v = []
        a = v.append
        a('<table class="calendar">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)

    def formatyear(self, theyear, width=3):
        """
        Return a formatted year as a table of tables.
        """
        v = []
        a = v.append
        width = max(width, 1)
        a('<table class="year">')
        a('\n')
        a('<tr><th colspan="%d" class="year">%s</th></tr>' % (width, theyear))
        for i in range(January, January + 12, width):
            # months in this row
            months = range(i, min(i + width, 13))
            a('<tr>')
            for m in months:
                a('<td>')
                a(self.formatmonth(theyear, m, withyear=False))
                a('</td>')
            a('</tr>')
        a('</table>')
        return ''.join(v)

    def formatyearpage(self, theyear, width=3, css='calendar.css', encoding=None):
        """
        Return a formatted year as a complete HTML page.
        """
        if encoding is None:
            encoding = sys.getdefaultencoding()
        v = []
        a = v.append
        a('<?xml version="1.0" encoding="%s"?>\n' % encoding)
        a('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')
        a('<html>\n')
        a('<head>\n')
        a('<meta http-equiv="Content-Type" content="text/html; charset=%s" />\n' % encoding)
        if css is not None:
            a('<link rel="stylesheet" type="text/css" href="%s" />\n' % css)
        a('<title>Calendar for %d</title>\n' % theyear)
        a('</head>\n')
        a('<body>\n')
        a(self.formatyear(theyear, width))
        a('</body>\n')
        a('</html>\n')
        return ''.join(v).encode(encoding, "xmlcharrefreplace")


class LibreBormeCalendar(HTMLCalendar):
    """
    Este calendario tiene enlaces al día si hay Borme.
    """

    def formatday(self, day, weekday):
        """
        Return a day as a table cell.
        """
        if day == self.day:
            css_selected = 'selected'
        else:
            css_selected = ''

        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        elif weekday in (5, 6):
            return '<td class="day %s %s">%d</td>' % (self.cssclasses[weekday], css_selected, day)
        elif self.today == datetime.date(self.year, self.month, day):
            if (self.month, day) in self.days_bormes:
                url = reverse('borme-fecha', args=['-'.join([str(self.year), str(self.month), str(day)])])
                return '<td class="day bormeday today %s"><a href="%s">%d</a></td>' % (css_selected, url, day)
            else:
                return '<td class="day nobormeday today %s">%d</td>' % (css_selected, day)
        else:
            if (self.month, day) in self.days_bormes:
                url = reverse('borme-fecha', args=['-'.join([str(self.year), str(self.month), str(day)])])
                return '<td class="day bormeday %s"><a href="%s">%d</a></td>' % (css_selected, url, day)
            else:
                return '<td class="day nobormeday %s">%d</td>' % (css_selected, day)

    def formatmonth(self, date):
        self.year = date.year
        self.month = date.month
        self.day = date.day
        self.today = datetime.date.today()

        _, lastday = monthrange(self.year, self.month)
        bormes = Borme.objects.filter(date__gte=datetime.date(self.year, self.month, 1), date__lte=datetime.date(self.year, self.month, lastday)).distinct('date').order_by('date')
        self.days_bormes = {}
        for borme in bormes:
            self.days_bormes[(borme.date.month, borme.date.day)] = borme

        return super(LibreBormeCalendar, self).formatmonth(self.year, self.month)


class LibreBormeAvailableCalendar(HTMLCalendar):
    """
    Este calendario tiene enlaces al Borme si existe para ese día.
    """

    def formatday(self, day, weekday):
        """
        Return a day as a table cell.
        Este calendario tiene enlaces al día si hay Borme.
        """

        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        elif weekday in (5, 6):
            return '<td class="day %s">%d</td>' % (self.cssclasses[weekday], day)
        elif self.today == datetime.date(self.year, self.month, day):
            if (self.month, day) in self.days_bormes:
                url = self.days_bormes[(self.month, day)].get_absolute_url()
                return '<td class="day bormeday today"><a href="%s">%d</a></td>' % (url, day)
            else:
                return '<td class="day nobormeday today">%d</td>' % day
        else:
            if (self.month, day) in self.days_bormes:
                url = self.days_bormes[(self.month, day)].get_absolute_url()
                return '<td class="day bormeday"><a href="%s">%d</a></td>' % (url, day)
            else:
                return '<td class="day nobormeday">%d</td>' % day

    def formatmonth(self, year, month, withyear=True):
        self.month = month
        return super(LibreBormeAvailableCalendar, self).formatmonth(year, month, withyear=withyear)

    def formatyear(self, theyear, bormes, width=3):
        self.year = theyear
        self.today = datetime.date.today()

        self.days_bormes = {}
        for borme in bormes:
            self.days_bormes[(borme.date.month, borme.date.day)] = borme

        return super(LibreBormeAvailableCalendar, self).formatyear(theyear, width=width)

/*
 * Code from: http://www.ecse.rpi.edu/Homepages/wrf/Research/Short_Notes/pnpoly.html
 *
 * Copyright (c) 1970-2003, Wm. Randolph Franklin
 *
 * Permission is hereby granted, free of charge, to any person obtaining 
 * a copy of this software and associated documentation files (the "Software"), 
 * to deal in the Software without restriction, including without limitation 
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, 
 * and/or sell copies of the Software, and to permit persons to whom the 
 * Software is furnished to do so, subject to the following conditions:
 *
 *   1. Redistributions of source code must retain the above copyright notice, 
 *      this list of conditions and the following disclaimers.
 *   2. Redistributions in binary form must reproduce the above copyright notice 
 *      in the documentation and/or other materials provided with the distribution.
 *   3. The name of W. Randolph Franklin may not be used to endorse or promote 
 *      products derived from this Software without specific prior written permission. 
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
 * INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
 * PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
 * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION 
 * OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. 
 */


/*
 * Documentation from: http://www.faqs.org/faqs/graphics/algorithms-faq/
 *
 * The code below is from Wm. Randolph Franklin <wrf@ecse.rpi.edu>
 * (see URL below) with some minor modifications for speed.  It returns 
 * 1 for strictly interior points, 0 for strictly exterior, and 0 or 1 
 * for points on the boundary.  The boundary behavior is complex but 
 * determined; in particular, for a partition of a region into polygons, 
 * each point is "in" exactly one polygon.  

 * (See p.243 of [O'Rourke (C)] for a discussion of boundary behavior.)
 */

/* This function was modified from having float arguments 
 * of the form: int pnpoly(int npol, float *xp, float *yp, float x, float y) 
 * to args having doubles. I hope this dosen't screw the algorith up
 * since I have no clue how it works
 *  - Josh
 */
int pnpoly(int npol, double *xp, double *yp, double x, double y)
{
    int i, j, c = 0;
    for (i = 0, j = npol-1; i < npol; j = i++) {
        if ((((yp[i]<=y) && (y<yp[j])) ||
                ((yp[j]<=y) && (y<yp[i]))) &&
            (x < (xp[j] - xp[i]) * (y - yp[i]) / (yp[j] - yp[i]) + xp[i]))

        c = !c;
    }
    return c;
}

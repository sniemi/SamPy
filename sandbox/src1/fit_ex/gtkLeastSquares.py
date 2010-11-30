#
# gtkLeastSquares.py : 	GUI for the module Scientific.Functions.LeastSquares
#		Implementation of the Levenberg-Marquardt algorithm for general
#		non-linear least-squares fits.
#
# Copyright (C) 2001 Adrian E. Feiguin <feiguin@ifir.edu.ar>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#


from string import *
from gtk import *
from Numeric import *
from Scientific.Functions.LeastSquares import *
from Scientific.Functions.FirstDerivatives import *

def fit_linear(parameters, values):
	a, b = parameters
	x = values
	return (a + b * x)

def fit_cuadratic(parameters, values):
	a, b, c, x0 = parameters
	x = values
	return(a + b * (x - x0) + c * (x - x0)**2)
	return

def fit_gauss(parameters, values):
	y0, x0, a, w = parameters
	x = values
	return(y0 + a * exp(-2*(x-x0)**2/w**2))
	return

def fit_lorentz(parameters, values):
	x0, y0, a, b = parameters
	x = values
	return(y0 + 2*a/pi * w / (4 * (x - x0)**2 + w**2))
	return

def fit_boltzman(parameters, values):
	x0, a1, a2, dx = parameters
	x = values
	return((a1 - a2)/(1 + exp((x - x0)/dx)) + a2)

def fit_logistic(parameters, values):
	x0, a1, a2, p = parameters
	x = values
	return((a1 - a2)/(1 + (x/x0)**p) + a2)

def fit_expdecay(parameters, values):
	x0, y0, a, t = parameters
	x = values
	return(y0 + a * exp(-(x - x0)/t))

def fit_expgrow(parameters, values):
	x0, y0, a, t = parameters
	x = values
	return(y0 + a * exp((x - x0)/t))

def fit_expassoc(parameters, values):
	y0, a1, t1, a2, t2 = parameters
	x = values
	return(y0 + a1 * (1 + exp(-x/t1)) + a2 * (1 + exp(-x/t2)))

def fit_hyperbl(parameters, values):
	p1, p2 = parameters
	x = values
	return(p1 * x/ (p2 + x))

def fit_pulse(parameters, values):
	x0, y0, a, t1, t2 = parameters
	x = values
	return(y0 + a * (1 + exp(-(x - x0)/t1)) * exp(-(x - x0)/t2))

def fit_rational0(parameters, values):
	a, b, c = parameters
	x = values
	return((b + c*x)/(1 + a*x))

def fit_sine(parameters, values):
	x0, a, w = parameters
	x = values
	return(a * sin(pi*(x - x0)/w))

def fit_gaussamp(parameters, values):
	x0, y0, a, w = parameters
	x = values
	return(y0 + a * exp(-(x - x0)**2/(2*w**2)))

def fit_allometric(parameters, values):
	a, b = parameters
	x = values
	return(a * x**b)



fit_linear_dic = {
	"Doc" : "Linear Function",
	"Exp" : "y = a + b * x",
	"Par" :	("a", "b"),
	"NumPar" : 2,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_linear
}
fit_cuadratic_dic = {
	"Doc" : "Cuadratic Function",
	"Exp" : "y = a + b * (x - x0) + c * (x - x0)**2",
	"Par" :	("a", "b", "c", "x0"),
	"NumPar" : 4,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_cuadratic
}
fit_gauss_dic = {
	"Doc" : "Amplitude version of Gaussian Function",
	"Exp" : "y = y0 + a * exp(-2*(x-x0)**2/w**2)",
	"Par" :	("x0", "y0", "a", "w"),
	"NumPar" : 4,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_gauss
}
fit_lorentz_dic = {
	"Doc" : "Lorentzian Peak Function",
	"Exp" : "y = y0 + 2*a/pi * w / (4 * (x - x0)**2 + w**2)",
	"Par" :	("x0", "y0", "a", "w"),
	"NumPar" : 4,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_lorentz
}
fit_boltzman_dic = {
	"Doc" : "Boltzman Function: sigmoidal curve",
	"Exp" : "y = (a1 - a2)/(1 + exp((x - x0)/dx)) + a2",
	"Par" :	("x0", "a1", "a2", "dx"),
	"NumPar" : 4,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_boltzman
}
fit_logistic_dic = {
	"Doc" : "Logistic dose/response",
	"Exp" : "y = (a1 - a2)/(1 + (x/x0)**p) + a2",
	"Par" :	("x0", "a1", "a2", "p"),
	"NumPar" : 4,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_logistic
}
fit_expdecay_dic = {
	"Doc" : "Exponential Decay",
	"Exp" : "y = y0 + a * exp(-(x - x0)/t)",
	"Par" :	("x0", "y0", "a", "t"),
	"NumPar" : 4,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_expdecay
}
fit_expgrow_dic = {
	"Doc" : "Exponential Growth",
	"Exp" : "y = y0 + a * exp((x - x0)/t)",
	"Par" :	("x0", "y0", "a", "t"),
	"NumPar" : 4,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_expgrow
}
fit_expassoc_dic = {
	"Doc" : "Exponential Associate",
	"Exp" : "y = y0 + a1 * (1 + exp(-x/t1)) + a2 * (1 + exp(-x/t2))",
	"Par" :	("y0", "a1", "t1", "a2", "t2"),
	"NumPar" : 5,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_expassoc
}
fit_hyperbl_dic = {
	"Doc" : "Hyperbola Function",
	"Exp" : "y = p1 * x/ (p2 + x)",
	"Par" :	("p1", "p2"),
	"NumPar" : 2,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_hyperbl
}
fit_pulse_dic = {
	"Doc" : "Pulse Function",
	"Exp" : "y = y0 + a * (1 + exp(-(x - x0)/t1)) * exp(-(x - x0)/t2)",
	"Par" :	("y0", "a", "t1", "t2"),
	"NumPar" : 4,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_pulse
}
fit_rational0_dic = {
	"Doc" : "Rational Function , type 0",
	"Exp" : "y = (b + c*x)/(1 + a*x)",
	"Par" :	("a", "b", "c"),
	"NumPar" : 3,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_rational0
}
fit_sine_dic = {
	"Doc" : "Sine Function",
	"Exp" : "y = a * sin(pi*(x - x0)/w)",
	"Par" :	("a", "x0", "w"),
	"NumPar" : 3,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_sine
}
fit_gaussamp_dic = {
	"Doc" : "Amplitude version of Gaussian Peak Function",
	"Exp" : "y = y0 + a * exp(-(x - x0)**2/(2*w**2))",
	"Par" :	("x0", "y0", "a", "w"),
	"NumPar" : 4,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_gaussamp
}
fit_allometric_dic = {
	"Doc" : "Classical Freundlich Model",
	"Exp" : "y = a * x**b",
	"Par" :	("a", "b"),
	"NumPar" : 4,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_allometric
}


functions = {
	"Linear" : fit_linear_dic,
	"Cuadratic" : fit_cuadratic_dic,
	"Gauss" : fit_gauss_dic,
	"Lorentz" : fit_lorentz_dic,
	"Boltzman" : fit_boltzman_dic,
	"Logistic" : fit_logistic_dic,
	"ExpDecay" : fit_expdecay_dic,
	"ExpGrow" : fit_expgrow_dic,
	"ExpAssoc" : fit_expassoc_dic,
	"Hyperbl" : fit_hyperbl_dic,
	"Pulse" : fit_pulse_dic,
	"Rational0" : fit_rational0_dic,
	"Sine" : fit_sine_dic,
	"GaussAmp" : fit_gaussamp_dic,
	"Allometric" : fit_allometric_dic
}

def fit(data):
	main_window = GtkWindow()
	main_window.set_title("Curve Fitting")
	main_window.set_border_width(5)
	main_window.connect("destroy", mainquit)
	main_window.connect("delete_event", mainquit)
	main_box = GtkVBox(FALSE, 5)
	main_window.add(main_box)
	main_frame = GtkFrame("Select Function")
	main_box.pack_start(main_frame)

	table = GtkTable(7, 4, FALSE)
	table.set_col_spacings(10)
	table.set_row_spacings(5)
	table.set_border_width(5)
	main_frame.add(table)

        swindow = GtkScrolledWindow()
        swindow.set_policy(POLICY_AUTOMATIC, POLICY_AUTOMATIC)
	swindow.set_usize(120, 100)
	table.attach(swindow, 0, 1, 0, 6)
        clist = GtkCList(1)
	swindow.add(clist)

	table.attach(GtkVSeparator(), 1, 2, 0, 6)

	text = map(lambda i: str(i), range(20))

	k = functions.keys()
	k.sort()
	for i in k:
		text[0] = i
		clist.append(text)

	label = GtkLabel("Exp:")
	label.set_alignment(1., .5)
	table.attach(label, 2, 3, 0, 1)
        fentry = GtkEntry()
#	fentry.set_editable(FALSE)
	table.attach(fentry, 3, 4, 0, 1)

	label = GtkLabel("Number of Param:")
	label.set_alignment(1., .5)
	table.attach(label, 2, 3, 1, 2)
        nspin = GtkSpinButton(GtkAdjustment(0, 0, 8, 1, 8, 0), 0, 0)
	nspin.set_editable(FALSE)
	nspin.set_state(STATE_INSENSITIVE)
	table.attach(nspin, 3, 4, 1, 2)

	label = GtkLabel("Param:")
	label.set_alignment(1., .5)
	table.attach(label, 2, 3, 2, 3)
        pentry = GtkEntry()
	pentry.set_editable(FALSE)
	pentry.set_state(STATE_INSENSITIVE)
	table.attach(pentry, 3, 4, 2, 3)

	label = GtkLabel("Independent Var:")
	label.set_alignment(1., .5)
	table.attach(label, 2, 3, 3, 4)
        iventry = GtkEntry()
	iventry.set_editable(FALSE)
	iventry.set_state(STATE_INSENSITIVE)
	table.attach(iventry, 3, 4, 3, 4)

	label = GtkLabel("Dependent Var:")
	label.set_alignment(1., .5)
	table.attach(label, 2, 3, 4, 5)
        dventry = GtkEntry()
	dventry.set_editable(FALSE)
	dventry.set_state(STATE_INSENSITIVE)
	table.attach(dventry, 3, 4, 4, 5)

	action_area = GtkHButtonBox()
	action_area.set_layout(BUTTONBOX_END)
	action_area.set_spacing(5)
	main_box.pack_start(action_area)
        fit_button = GtkButton("Fit")
	action_area.pack_start(fit_button)
        close_button = GtkButton("Close")
	action_area.pack_start(close_button)

	lframe = GtkFrame()
	lframe.set_shadow_type(SHADOW_IN)
	main_box.pack_start(lframe)
	explabel = GtkLabel("Choose a Fitting Function")
	lframe.add(explabel)



#	CALLBACK FUNCTIONS
	def select_function(_clist, row, col, event, functions = functions, label = explabel, fentry = fentry, pentry = pentry, nspin = nspin, iventry = iventry, dventry = dventry):
		k = _clist.get_text(row, col)
                f = functions[k]
		label.set_text(f["Doc"])
		fentry.set_text(f["Exp"])
		nspin.set_value(f["NumPar"])
		iventry.set_text(f["IVar"])
		dventry.set_text(f["DVar"])
		s = ""
		for i in f["Par"]:
			s = s + i + ", "
		pentry.set_text(s[:len(s)-2])

	def open_fit_dialog(_button, functions = functions, clist = clist, data = data):
		a = clist.__getattr__("selection")
		k = clist.get_text(a[0], 0)
		f = functions[k]
		param = (1, 1)
		fit_dialog(f, data)


# 	CONNECT OBJECTS

	clist.connect("select_row", select_function)

	fit_button.connect("clicked", open_fit_dialog)
	close_button.connect("clicked", main_window.destroy)

        clist.select_row(0, 0)
	main_window.show_all()
	mainloop()

def fit_dialog(f, data):
	main_window = GtkWindow()
	main_window.set_title("Fit")
	main_window.set_border_width(5)
	main_window.connect("destroy", mainquit)
	main_window.connect("delete_event", mainquit)
	table = GtkTable(len(f["Par"])+3, 2, FALSE)
	table.set_col_spacings(10)
	table.set_row_spacings(5)
	main_window.add(table)

	table.attach(GtkLabel("Variable"), 0, 1, 0, 1)
	table.attach(GtkLabel("Value"), 1, 2, 0, 1)
	table.attach(GtkHSeparator(), 0, 2, 1, 2)
	r = 2
	entries = []
	for i in f["Par"]:
#		check = GtkCheckButton(i+":")
#		table.attach(check, 0, 1, r, r+1)
		table.attach(GtkLabel(i+":"), 0, 1, r, r+1)
		entry = GtkEntry()
		entries = entries + [entry]
		entry.set_text("0.0")
		table.attach(entry, 1, 2, r, r+1)
		r = r + 1

	table.attach(GtkHSeparator(), 0, 2, r, r + 1)
	r = r + 1
	table.attach(GtkLabel("Chi_Sqr:"), 0, 1, r, r + 1)
	err_entry = GtkEntry()
	table.attach(err_entry, 1, 2, r, r + 1)
	r = r + 1
	table.attach(GtkHSeparator(), 0, 2, r, r + 1)

	def run_fit(_button, f = f, data = data, entries = entries, err_entry = err_entry):
		n = 0
		p = ()
		for i in entries:
			s = entries[n].get_text()
			p = p + (atof(s),)
			n = n + 1

		fit, error = leastSquaresFit(f["Function"], p, data)

		n = 0
		for i in entries:
			entries[n].set_text(str(fit[n]))
			n = n + 1

		err_entry.set_text(str(error))
#		print "Fitted parameters: ", fit
#		print "Fit error: ", error

		return


	action_area = GtkHButtonBox()
	action_area.set_layout(BUTTONBOX_SPREAD)
	action_area.set_spacing(5)
	run_button = GtkButton("Run")
	close_button = GtkButton("Close")
	action_area.pack_start(run_button)
	action_area.pack_start(close_button)
	table.attach(action_area, 0, 2, r + 1, r + 2)

#	CONNECT OBJECTS

	run_button.connect("clicked", run_fit)
	close_button.connect("clicked", main_window.destroy)

	main_window.show_all()
	mainloop()


# Test for linear fit:
#
# from gtkLeastSquares import *
data = [ (0., 0.), (1., 1.1), (2., 1.98), (3., 3.05) ]
fit(data)

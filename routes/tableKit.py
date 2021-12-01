from flask import Blueprint, redirect, render_template, session
import json

tableKit = Blueprint('tableKit', __name__)


@tableKit.route("/")
def setup():
    return render_template("kit_console.html")


@tableKit.route("/available")
def dashBoard():
    if session.get('tableId') is not None:
        return render_template("kit_available.html")
    else:
        return redirect("/tableKit/")


@tableKit.route("/claimed")
def claimed():
    if session.get('bookingId') is not None:
        return render_template("kit_dashboard.html")
    return redirect("/tableKit/available")


@tableKit.route("/reserved")
def reserved():
    if session.get('bookingId') is not None:
        return render_template("kit_reserved.html")
    return redirect("/tableKit/available")

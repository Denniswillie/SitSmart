from flask import Blueprint, request, redirect, render_template, session
import json

tableKit = Blueprint('tableKit', __name__)


@tableKit.route("/setup")
def setup():
    return render_template("")


@tableKit.route("/dashboard")
def dashBoard():
    return render_template("")


@tableKit.route("/claimed")
def claimed():
    return render_template("")


@tableKit.route("/reserved")
def reserved():
    return render_template("")

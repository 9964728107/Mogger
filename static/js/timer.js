let step = 1;
let loops = Math.round(100 / step);
let increment = 360 / loops;
let half = Math.round(loops / 2);
let barColor = "#ec366b";
let backColor = "#feeff4";

$(function () {
  clock.init();
});

clock = {
  interval: null,
  init: function () {
    $(".input-btn").click(function () {
      switch ($(this).data("action")) {
        case "start":
          clock.stop();
          clock.start($(".input-num").val());
          break;
        case "stop":
          clock.stop();
          break;
      }
    });
  },
  start: function (t) {
    let time = t ? t * 60 : 1 * 60;
    let count = 0;
    let interval = 1000;
    $(".count").text(time / 60);
    if (time > 60) {
      $(".count").addClass("min");
    } else {
      $(".count").addClass("sec");
    }
    clock.interval = setInterval(function () {
      time = time - 1;
      count = count + 1;
      if (time > 0) {
        $(".count").text(time / 60);
      } else {
        $(".count").text(0);
        clearInterval(clock.interval);
      }
      let pie = (100 * count) / (loops * (time / 60));
      let deg = (pie / 100) * 360;
      if (deg >= 180) {
        deg = 180 - (deg - 180);
      }
      let nextdeg =
        deg + (count % 2 === 0 ? increment : -increment) * half + "deg";
      $(".clock").css({
        "background-image":
          "linear-gradient(" +
          nextdeg +
          "," +
          barColor +
          " 50%,transparent 50%,transparent),linear-gradient(270deg," +
          barColor +
          " 50%," +
          backColor +
          " 50%," +
          backColor +
          ")",
      });
    }, interval);
  },
  stop: function () {
    clearInterval(clock.interval);
    $(".count").text(0);
    $(".clock").removeAttr("style");
  },
};

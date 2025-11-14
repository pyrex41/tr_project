module Components.Chart exposing (barChart, pieChart)

import Chart as C
import Chart.Attributes as CA
import Html exposing (Html)
import Types exposing (ChartData)


-- BAR CHART


barChart : List ChartData -> Html msg
barChart data =
    C.chart
        [ CA.height 300
        , CA.width 500
        ]
        [ C.xTicks []
        , C.yTicks []
        , C.xLabels [ CA.moveDown 10 ]
        , C.yLabels [ CA.moveLeft 10 ]
        , C.xAxis []
        , C.yAxis []
        , C.bars []
            [ C.bar .value [ CA.roundTop 0.2 ] ]
            data
        ]


-- PIE CHART (using bars as approximation)
-- Note: elm-charts 5.0 doesn't have native pie charts


pieChart : List ChartData -> Html msg
pieChart data =
    let
        total =
            List.sum (List.map .value data)

        percentages =
            List.map (\item -> { item | value = (item.value / total) * 100 }) data
    in
    C.chart
        [ CA.height 300
        , CA.width 500
        ]
        [ C.xTicks []
        , C.yTicks []
        , C.xLabels [ CA.moveDown 10 ]
        , C.yLabels [ CA.moveLeft 10 ]
        , C.xAxis []
        , C.yAxis []
        , C.bars []
            [ C.bar .value [ CA.roundTop 0.2 ] ]
            percentages
        ]

module Components.OrderCard exposing (view)

import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (onClick)
import Types exposing (OrderCard)


type alias Config msg =
    { order : OrderCard
    , onSelect : Int -> msg
    }


view : Config msg -> Html msg
view config =
    div
        [ class "bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition cursor-pointer"
        , onClick (config.onSelect config.order.id)
        ]
        [ h3 [ class "text-xl font-bold text-blue-900 mb-2" ]
            [ text config.order.caseName ]
        , div [ class "flex items-center gap-4 text-sm text-gray-600 mb-3" ]
            [ case config.order.date of
                Just date ->
                    span [ class "flex items-center" ]
                        [ text date ]

                Nothing ->
                    text ""
            , if not (List.isEmpty config.order.expertNames) then
                span [ class "flex items-center" ]
                    [ text (String.join ", " config.order.expertNames) ]

              else
                text ""
            ]
        , p [ class "text-gray-700 line-clamp-3" ]
            [ text config.order.summary ]
        , div [ class "mt-4 pt-4 border-t border-gray-200" ]
            [ span [ class "text-sm text-blue-600 font-semibold hover:text-blue-800" ]
                [ text "View Details ->" ]
            ]
        ]

module Main exposing (main)

import Browser
import Browser.Navigation as Nav
import Components.Layout
import Html exposing (..)
import Html.Attributes exposing (..)
import Pages.Dashboard
import Pages.OrderDetail
import Pages.Search
import Url
import Url.Parser as Parser exposing ((</>), Parser, int, oneOf, top)


-- MAIN


main : Program Flags Model Msg
main =
    Browser.application
        { init = init
        , view = view
        , update = update
        , subscriptions = subscriptions
        , onUrlChange = UrlChanged
        , onUrlRequest = LinkClicked
        }


-- MODEL


type alias Flags =
    { apiBaseUrl : String
    }


type alias Model =
    { key : Nav.Key
    , url : Url.Url
    , apiBaseUrl : String
    , page : Page
    }


type Page
    = Dashboard Pages.Dashboard.Model
    | Search Pages.Search.Model
    | OrderDetail Pages.OrderDetail.Model
    | NotFound


init : Flags -> Url.Url -> Nav.Key -> ( Model, Cmd Msg )
init flags url key =
    let
        ( page, pageCmd ) =
            initPage flags.apiBaseUrl (urlToRoute url)
    in
    ( { key = key
      , url = url
      , apiBaseUrl = flags.apiBaseUrl
      , page = page
      }
    , pageCmd
    )


initPage : String -> Route -> ( Page, Cmd Msg )
initPage apiBaseUrl route =
    case route of
        DashboardRoute ->
            let
                ( dashboardModel, dashboardCmd ) =
                    Pages.Dashboard.init apiBaseUrl
            in
            ( Dashboard dashboardModel
            , Cmd.map DashboardMsg dashboardCmd
            )

        SearchRoute ->
            let
                ( searchModel, searchCmd ) =
                    Pages.Search.init apiBaseUrl ""
            in
            ( Search searchModel
            , Cmd.map SearchMsg searchCmd
            )

        OrderDetailRoute orderId ->
            let
                ( orderDetailModel, orderDetailCmd ) =
                    Pages.OrderDetail.init apiBaseUrl orderId
            in
            ( OrderDetail orderDetailModel
            , Cmd.map OrderDetailMsg orderDetailCmd
            )

        NotFoundRoute ->
            ( NotFound, Cmd.none )


-- ROUTING


type Route
    = DashboardRoute
    | SearchRoute
    | OrderDetailRoute Int
    | NotFoundRoute


urlToRoute : Url.Url -> Route
urlToRoute url =
    Parser.parse routeParser url
        |> Maybe.withDefault NotFoundRoute


routeParser : Parser (Route -> a) a
routeParser =
    oneOf
        [ Parser.map DashboardRoute top
        , Parser.map SearchRoute (Parser.s "search")
        , Parser.map OrderDetailRoute (Parser.s "order" </> int)
        ]


-- UPDATE


type Msg
    = LinkClicked Browser.UrlRequest
    | UrlChanged Url.Url
    | NavigateTo String
    | DashboardMsg Pages.Dashboard.Msg
    | SearchMsg Pages.Search.Msg
    | OrderDetailMsg Pages.OrderDetail.Msg


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        LinkClicked urlRequest ->
            case urlRequest of
                Browser.Internal url ->
                    ( model, Nav.pushUrl model.key (Url.toString url) )

                Browser.External href ->
                    ( model, Nav.load href )

        UrlChanged url ->
            let
                route =
                    urlToRoute url

                ( newPage, pageCmd ) =
                    initPage model.apiBaseUrl route
            in
            ( { model | url = url, page = newPage }
            , pageCmd
            )

        NavigateTo path ->
            ( model, Nav.pushUrl model.key path )

        DashboardMsg dashboardMsg ->
            case model.page of
                Dashboard dashboardModel ->
                    let
                        ( newDashboardModel, dashboardCmd ) =
                            Pages.Dashboard.update dashboardMsg dashboardModel

                        -- Handle search submission navigation
                        navigationCmd =
                            case dashboardMsg of
                                Pages.Dashboard.SearchSubmitted ->
                                    if String.isEmpty newDashboardModel.searchQuery then
                                        Cmd.none

                                    else
                                        Nav.pushUrl model.key "/search"

                                _ ->
                                    Cmd.none
                    in
                    ( { model | page = Dashboard newDashboardModel }
                    , Cmd.batch
                        [ Cmd.map DashboardMsg dashboardCmd
                        , navigationCmd
                        ]
                    )

                _ ->
                    ( model, Cmd.none )

        SearchMsg searchMsg ->
            case model.page of
                Search searchModel ->
                    let
                        ( newSearchModel, searchCmd ) =
                            Pages.Search.update searchMsg searchModel

                        -- Handle order selection navigation
                        navigationCmd =
                            case searchMsg of
                                Pages.Search.OrderSelected orderId ->
                                    Nav.pushUrl model.key ("/order/" ++ String.fromInt orderId)

                                _ ->
                                    Cmd.none
                    in
                    ( { model | page = Search newSearchModel }
                    , Cmd.batch
                        [ Cmd.map SearchMsg searchCmd
                        , navigationCmd
                        ]
                    )

                _ ->
                    ( model, Cmd.none )

        OrderDetailMsg orderDetailMsg ->
            case model.page of
                OrderDetail orderDetailModel ->
                    let
                        ( newOrderDetailModel, orderDetailCmd ) =
                            Pages.OrderDetail.update orderDetailMsg orderDetailModel
                    in
                    ( { model | page = OrderDetail newOrderDetailModel }
                    , Cmd.map OrderDetailMsg orderDetailCmd
                    )

                _ ->
                    ( model, Cmd.none )


-- SUBSCRIPTIONS


subscriptions : Model -> Sub Msg
subscriptions _ =
    Sub.none


-- VIEW


view : Model -> Browser.Document Msg
view model =
    { title = pageTitle model.page
    , body =
        [ Components.Layout.view
            { currentPage = pageToPath model.page
            , onNavigate = NavigateTo
            }
            (viewPage model)
        ]
    }


pageTitle : Page -> String
pageTitle page =
    case page of
        Dashboard _ ->
            "Dashboard - Legal Document Analysis"

        Search _ ->
            "Search - Legal Document Analysis"

        OrderDetail _ ->
            "Order Detail - Legal Document Analysis"

        NotFound ->
            "Not Found - Legal Document Analysis"


pageToPath : Page -> String
pageToPath page =
    case page of
        Dashboard _ ->
            "/"

        Search _ ->
            "/search"

        OrderDetail orderDetailModel ->
            "/order/" ++ String.fromInt orderDetailModel.orderId

        NotFound ->
            "/not-found"


viewPage : Model -> List (Html Msg)
viewPage model =
    case model.page of
        Dashboard dashboardModel ->
            [ Pages.Dashboard.view dashboardModel DashboardMsg NavigateTo ]

        Search searchModel ->
            [ Pages.Search.view searchModel SearchMsg (\orderId -> NavigateTo ("/order/" ++ String.fromInt orderId)) ]

        OrderDetail orderDetailModel ->
            [ Pages.OrderDetail.view orderDetailModel OrderDetailMsg ]

        NotFound ->
            [ h1 [ class "text-3xl font-bold text-red-600 mb-6" ]
                [ text "404 - Page Not Found" ]
            , p [ class "text-gray-700 mb-4" ]
                [ text "The page you are looking for does not exist." ]
            , a
                [ class "text-blue-600 hover:text-blue-800 font-semibold"
                , href "/"
                ]
                [ text "Go to Dashboard" ]
            ]

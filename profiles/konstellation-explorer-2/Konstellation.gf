abstract Konstellation = {
 flags startcat = Output ;
 cat Output ;
 fun
  PresentClassification : String -> String -> Output ;
  PresentReadContext : String -> String -> String -> Output ;
  PresentResultPage : String -> String -> String -> String -> String -> Output ;
  PresentReportedAssertion : String -> String -> String -> Output ;
  PresentAttribute : String -> String -> Output ;
  PresentEntity : String -> String -> Output ;
  PresentFilterUnary : String -> String -> Output ;
  PresentFilterValues : String -> String -> String -> Output ;
  PresentSelectionIdentities : String -> String -> Output ;
  PresentSelectionLink : String -> String -> String -> Output ;
  PresentFilterOverlap : String -> String -> String -> String -> Output ;
}

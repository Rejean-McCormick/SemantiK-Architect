concrete KonstellationFre of Konstellation = {
 lincat Output = {s : Str} ;
 lin
  PresentClassification label value = {s = label.s ++ ":" ++ value.s} ;
  PresentReadContext label dataset policy = {s = label.s ++ "— données :" ++ dataset.s ++ "; politique :" ++ policy.s} ;
  PresentResultPage label members total pageCount hasMore = {s = label.s ++ ":" ++ members.s ++ "— total :" ++ total.s ++ "; cette page :" ++ pageCount.s ++ "; suite :" ++ hasMore.s} ;
  PresentReportedAssertion agent predicate patient = {s = agent.s ++ "—" ++ predicate.s ++ ":" ++ patient.s} ;
  PresentAttribute label value = {s = label.s ++ ":" ++ value.s} ;
  PresentEntity label entity = {s = label.s ++ ":" ++ entity.s} ;
  PresentFilterUnary label relation = {s = label.s ++ ":" ++ relation.s} ;
  PresentFilterValues label relation values = {s = label.s ++ "—" ++ relation.s ++ ":" ++ values.s} ;
  PresentSelectionIdentities label values = {s = label.s ++ ":" ++ values.s} ;
  PresentSelectionLink label relation target = {s = label.s ++ "—" ++ relation.s ++ ":" ++ target.s} ;
  PresentFilterOverlap label relation interval match = {s = label.s ++ "—" ++ relation.s ++ ":" ++ interval.s ++ "; correspondance :" ++ match.s} ;
}

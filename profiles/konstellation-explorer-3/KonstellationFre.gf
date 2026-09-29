concrete KonstellationFre of Konstellation = {
 flags unlexer = text ;
 lincat Output = {s : Str} ; NP = {s : Str} ; V2 = {s : Str} ; ClassNP = {s : Str} ;
 lin
  RealizeTransitive agent predicate patient = {s = agent.s ++ predicate.s ++ patient.s ++ "."} ;
  RealizeClassification entity class = {s = entity.s ++ "est" ++ class.s ++ "."} ;

  Augustin_NP = {s = "Augustin"} ;
  Foi_NP = {s = "La foi"} ;
  LeonXIII_NP = {s = "Léon XIII"} ;
  JeanPaulII_NP = {s = "Jean-Paul II"} ;
  ImmaculeeConception_NP = {s = "L’Immaculée Conception"} ;

  Defendre_V2 = {s = "défend"} ;
  Stimuler_V2 = {s = "stimule"} ;
  Affirmer_V2 = {s = "affirme"} ;

  ExistenceLibreArbitre_NP = {s = "l’existence du libre arbitre"} ;
  EnqueteIntellectuelleAnselme_NP = {s = "l’enquête intellectuelle d’Anselme"} ;
  ProprietePriveePrevoyanceFamille_NP = {s = "la propriété privée comme moyen de prévoyance et de protection de la famille"} ;
  PrioriteTravailCapital_NP = {s = "la priorité du travail sur le capital dans le processus de production"} ;

  Dogme_ClassNP = {s = "un dogme"} ;
}

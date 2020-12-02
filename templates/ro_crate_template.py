RO_CRATE_TEMPLATE ="""{
  "@context": [
    "https://researchobject.github.io/ro-crate/1.0/context.jsonld",
    {
      "@vocab": "http://schema.org/"
    }
  ],
  "@graph": [
    {
      "@id": "./",
      "@type": "Dataset",
      "author": [
        {
          "@id": "https://orcid.org/0000-0001-5364-9936"
        },
        {
          "@id": "https://orcid.org/0000-0001-7096-1307"
        }
      ],
      "contactPoint": {
        "@id": "Penelope.Ajani@uts.edu.au"
      },
      "datePublished": "2020-07-15",
      "month": "August",
      "description": "A collection of salinity data readings from Camden Haven for June 2020",
      "hasPart": [
        {
          "@id": "Data/"
        }
      ],
      "contentLocation": {
        "@id": "https://sws.geonames.org/8210175/"
      },
      "name": "NSW Estuary Salinity Data - Camden Haven - June 2020"
    },
    {
      "@id": "Data/",
      "@type": "Dataset",
      "description": "Sensor data from Camden Haven",
      "hasPart": {
        "@id": "Data/out_NSW_CH_01_June2020.csv"
      },
      "name": "Data",
      "temporalCoverage": "2020-06"
    },
    {
      "@id": "Data/out_NSW_CH_01_June2020.csv",
      "@type": "File",
      "description": "The raw sensor data from Camden Haven - could include anomalies",
      "name": "Raw Data - June 2020"
    },
    {
      "@id": "Penelope.Ajani@uts.edu.au",
      "@type": "ContactPoint",
      "email": "Penelope.Ajani@uts.edu.au",
      "name": "Penelope Ajani"
    },
    {
      "@id": "_:b0",
      "@type": "GeoCoordinates",
      "latitude": "-31.6485",
      "longitude": "152.8346",
      "name": "Camden Haven"
    },
    {
      "@id": "https://orcid.org/0000-0001-5364-9936",
      "@type": "Person",
      "FamilyName": "Ajani",
      "affiliation": {
        "@id": "https://ror.org/03f0f6041"
      },
      "givenName": "Penelope",
      "name": "Penelope Ajani"
    },
    {
      "@id": "https://orcid.org/0000-0001-7096-1307",
      "@type": "Person",
      "FamilyName": "Murray",
      "affiliation": {
        "@id": "https://ror.org/03f0f6041"
      },
      "givenName": "Shauna",
      "name": "Shauna Murray"
    },
    {
      "@id": "https://ror.org/03f0f6041",
      "@type": "Organization",
      "Description": "The University of Technology Sydney is a public research university located in Sydney, Australia",
      "name": "University of Technology Sydney"
    },
    {
      "@id": "https://sws.geonames.org/8210175/",
      "@type": "Place",
      "geo": {
        "@id": "_:b0"
      },
      "name": "Camden Haven"
    },
    {
      "@id": "https://www.nationalarchives.gov.uk/PRONOM/fmt/214",
      "@type": "website",
      "name": "Microsoft Excel for Windows"
    },
    {
      "@id": "https://www.nationalarchives.gov.uk/PRONOM/x-fmt/18",
      "@type": "website",
      "name": "Comma Separated Values"
    },
    {
      "@id": "ro-crate-metadata.json",
      "@type": "CreativeWork",
      "about": {
        "@id": "./"
      },
      "identifier": "ro-crate-metadata.json"
    }
  ]
}"""

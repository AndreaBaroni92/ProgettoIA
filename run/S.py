schemaRequest = {  #schema per convalidare le richieste
   "VNFs":{  #duplist mettere solo dpi
      "type":"array",
      "items":{  
         "type":"string",
         "enum":[  
            "DPI",
            "NAT",
            "TS",
            "WANA",
            "VPN"
         ]
      }
   },
   "Mask":{  
      "type":"array",
      "items":{  
         "type":"boolean"
      }
   },
   "type":"object",
   "properties":{  
      "src":{  
         "type":"integer"
      },
      "dst":{  
         "type":"integer"
      },
      "qos":{  
         "type":"string"
      },
      "qos_type":{  
         "type":"string"
      },
      "qos_thr":{  
         "type":"string"
      },
      "qos_value":{  
         "type":"integer"
      },
      "vnfList":{  
         "$ref":"#/VNFs"
      },
      "dupList":{  
         "$ref":"#/VNFs"
      },
      "prox_to_src":{  
         "$ref":"#/Mask"
      },
      "prox_to_dst":{  
         "$ref":"#/Mask"
      }
   },

   "additionalProperties": False,
   "required":["src","dst","vnfList","dupList","prox_to_src","prox_to_dst"]
}

schemaDomConst = {
   "type":"array",
   "items":{
      "type":"array",
      "maxItems":4,
      "minItems":4,
      "items":[
         {"type":"integer",  "description":"a domain name"},
         {"type":"string", "enum":["DPI","NAT","TS","WANA","VPN"] },
         {"type":"integer", "description":"VFN type minimum quantity"},
         {"type":"integer", "description":"VFN type maximum quantity"}
         ]
   }

}
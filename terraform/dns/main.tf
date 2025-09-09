variable "records_yaml" { type = string }
variable "compartment_ocid" { type = string }

locals {
  raw = yamldecode(file(var.records_yaml))

  # 1) 正規化: 末尾ドット・大文字化・TTLデフォルト・trim/sort
  canonical = [
    for r in local.raw : {
      name  = endswith(r.name, ".") ? r.name : "${r.name}."
      type  = upper(r.type)
      ttl   = try(r.ttl, 300)
      rdata = sort([for v in r.rdata : trim(v)]) # 並びを固定
    }
  ]

  # 2) (name, type) ごとに RRset を形成
  rrsets = {
    for r in local.canonical :
    "${r.name}|${r.type}" => {
      name = r.name
      type = r.type
      items = [for d in r.rdata : {
        domain = r.name
        rtype  = r.type
        ttl    = r.ttl
        rdata  = d
      }]
    }
  }
}

resource "oci_dns_zone" "zone" {
  name           = "example.com"
  zone_type      = "PRIMARY"
  compartment_id = var.compartment_ocid
}

# 3) RRset 単位で apply（items は正規化済みで順序安定）
resource "oci_dns_rrset" "good" {
  for_each = local.rrsets

  zone_name_or_id = oci_dns_zone.zone.id
  domain          = each.value.name
  rtype           = each.value.type

  dynamic "items" {
    for_each = each.value.items
    content {
      domain = items.value.domain
      rtype  = items.value.rtype
      ttl    = items.value.ttl
      rdata  = items.value.rdata
    }
  }
}

variable "compartment_ocid" { type = string }

variable "records_yaml" {
  type        = string
  description = "YAMLファイルのパス、または YAML 文字列（base64でも可）"
}

locals {
  # 2) base64 ならデコード、そうでなければそのまま
  yaml_plain = base64decode(var.records_yaml)

  # 3) YAML をデコード
  raw = yamldecode(local.yaml_plain)

  canonical = [
    for r in local.raw : {
      name = endswith(r.name, ".") ? r.name : "${r.name}."
      type = upper(r.type)
      ttl  = try(r.ttl, 300)

      # ここを修正：trim → trimspace、ついでに型安定化
      rdata = sort([
        for v in tolist(r.rdata) : trimspace(tostring(v))
      ])
    }
  ]

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
  scope          = "PRIVATE"
  compartment_id = var.compartment_ocid
}

# items は「引数」ではなく「ブロック」なので dynamic で展開
resource "oci_dns_rrset" "good" {
  for_each        = local.rrsets
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

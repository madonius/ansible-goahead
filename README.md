# goahead

Ansible role to query [xorpaul](https://github.com/xorpaul)'s goahead server whether this machine is safe to restart or not.

## Requirements

__None__

## Role Variables

### Mandatory

* **goahead_service_url** the service's URL __example: https://goahead-service.domain.tld/__
* **goahead_service_url_ca_file** the certificate to authenticate agains the server __example: /etc/ssl/certs/optional-ca.pem__

### Optional

| Option 			| Description 		| Default value |
| :---   			| :---        		| :---          |
| goahead_requesting_fqdn 	| the requested fqdn 	| `{{ ansible_fqdn }}` |

## Dependencies

__None__

# Example Playbook

```yaml
- hosts: servers
  roles:
    - role: goahead_service_url
```

## License

MIT

## Author Information

* [/madonius](https://github.com/madonius)

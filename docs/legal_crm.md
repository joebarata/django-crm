# Legal CRM Module

The Legal CRM module provides specialized tooling for law firms to manage cases, clients, deadlines, finances and documents from a single interface. The feature set extends the core CRM with workflows tailored to the Brazilian legal market, including support for tribunals, official diary updates and LGPD-compliant access controls.

## Key features

- **Gestão de Casos e Processos**: Cadastro completo de processos com partes envolvidas, tribunal, vara e assunto. A linha do tempo processual permite registrar audiências, petições e integrações automáticas com diários oficiais.
- **Gestão de Clientes e Contatos**: Perfis unificados de clientes pessoa física ou jurídica, incluindo documentos, área de atuação e notas de relacionamento.
- **Agenda e Controle de Prazos**: Deadlines vinculados a processos, alertas críticos e calendário mensal com visualização agrupada por dia.
- **Gestão Financeira**: Contratos de honorários com diferentes modelos (fixo, êxito, hora, assinatura), controle de parcelas e status de recebimento.
- **Documentos e Automação**: Repositório seguro com versionamento básico, geração de regras de automação e registro de integrações externas.
- **Relatórios e Inteligência**: Dashboard com indicadores de casos abertos, prazos, faturamento previsto e taxa de êxito estimada.
- **Segurança e Conformidade**: Controles de acesso por usuário e auditoria de ações com metadados.

## Navegação

| Página | Caminho | Descrição |
| --- | --- | --- |
| Dashboard | `/123/legal/dashboard/` | Indicadores em tempo real, prazos e audiências.
| Casos | `/123/legal/cases/` | Lista de processos com filtros rápidos por status.
| Detalhe do caso | `/123/legal/cases/<id>/` | Linha do tempo, documentos, prazos e regras do caso.
| Clientes | `/123/legal/clients/` | Cadastro completo de clientes.
| Agenda | `/123/legal/calendar/` | Visão mensal de prazos processuais.
| Financeiro | `/123/legal/finance/agreements/` | Contratos de honorários e parcelas.

> Obs.: O prefixo `123/` corresponde à configuração `SECRET_CRM_PREFIX` do projeto e pode ser alterado conforme necessário.

## Próximos passos sugeridos

1. Configurar integrações com diários oficiais e tribunais na área de *Fontes de Integração* (administração).
2. Habilitar envios de alerta via e-mail, SMS ou aplicativo utilizando as filas existentes do projeto.
3. Criar modelos de documentos (contratos e peças) e associá-los a automatizações de caso.
4. Ajustar a base de dados para o banco utilizado em produção (MySQL ou PostgreSQL) antes de executar as migrações.

## Migrações

Execute as migrações do novo aplicativo após configurar o banco de dados:

```bash
python manage.py migrate legal
```

## Testes rápidos

- `python manage.py check` — valida a configuração do projeto (em ambientes sem MySQL haverá avisos relacionados ao agendador de e-mails).

## Conformidade LGPD

- Todos os modelos herdam metadados de criação/modificação.
- Controles de acesso com expiração permitem segmentar visualização de dados sensíveis.
- Logs de auditoria registram alterações e atividades por usuário.

## Recursos adicionais

- Admin do Django customizado com inlines para linha do tempo, prazos e documentos.
- Formulários com componentes Bootstrap para experiência consistente com o restante do CRM.

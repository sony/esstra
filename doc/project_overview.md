# Project Overview

## Table of Contents
1. Introduction
2. Background of Development
3. Purpose and Design Philosophy
4. Features and Strengths
5. Reason for Open Sourcing
6. References & Related Links

## 1. Introduction
This document provides an overview of Project ESSTRA, including its background, objectives, design philosophy, strengths, and the reasons for making it open source.

ESSTRA is a software suite developed to enhance transparency and traceability in the software supply chain.
It enables embedding actual source file information (such as file names, hashes, and licenses) into binaries, allowing recipients to directly verify the composition of delivered software.

With the increasing use of Open Source Software (OSS) and growing demands for Software Bill of Materials (SBOM) quality and regulatory compliance, challenges such as “not knowing what’s inside” and “difficulty verifying composition or license information when only binaries are delivered” have become apparent.

ESSTRA was designed and developed to address these issues and improve overall supply chain quality.
This document explains its background, design philosophy, features, and the significance of open-sourcing in detail.

## 2. Background of Development
Recently, the importance of transparency and traceability throughout the software supply chain has increased.
With the expansion of OSS usage, there are more situations requiring SBOM quality, license compliance, and regulatory response.

In May 2021, the U.S. issued an Executive Order to improve national cybersecurity.
In September 2022, the European Commission proposed the Cyber Resilience Act (CRA), accelerating efforts to strengthen supply chain management.

On the ground, various challenges have emerged.
For example, hardware vendors may deliver Board Support Package (BSP) as binaries only, without accompanying source code, or even if source code is provided, reproducible builds may not be possible.
There are also difficulties in verifying whether delivered binaries and SBOMs truly match.

Sometimes, binaries may contain source files with unintended licenses, or files with licenses different from those declared by the author may be mixed in, making accurate license information verification difficult.

To address these issues, methods such as build log and Makefile analysis, manual file checks, and license scanner full scans have been used.
Package management system metadata, delivery documents, and SBOM/configuration information from suppliers or developers are also utilized.

Automated SBOM generation tools and binary analysis tools are widely used, but many rely on source code or package management information.
Automatically matching and verifying binaries with SBOM contents often requires additional effort and customization for each environment.

Given these circumstances, a new approach is needed to resolve the “not knowing what’s inside” problem and achieve overall supply chain quality improvement.

## 3. Purpose and Design Philosophy
ESSTRA aims to technically enhance transparency and traceability in the software supply chain.

By embedding actual source file information (file names, hashes, licenses, etc.) into binaries, it enables recipients to directly obtain and verify composition information from the binary alone.
This information is stored in a dedicated ELF section, does not affect executable code or linking results, and the binary operates identically regardless of ESSTRA’s presence.

ESSTRA is designed to be independent of specific development frameworks or environments.
It can be introduced, operated, and verified standalone, and flexibly adapted to various situations and needs.
It can also be integrated with other SBOM management or software supply chain management systems, and used alongside various methods and tools to meet diverse requirements.

ESSTRA considers interoperability with standard formats such as SPDX, aiming to accurately transmit composition information from upstream in the supply chain, enabling downstream recipients to verify and explain the software themselves, thereby enhancing transparency and reliability.

## 4. Features and Strengths
ESSTRA is designed with practicality and flexibility to address diverse challenges and operational needs.
Key features and strengths include:

- Build framework independent and easy to integrate
  - ESSTRA is independent of specific development frameworks or environments.
  It collects source file hashes during compilation, regardless of the build system, and embeds metadata directly into the binary.
  Integration into existing CI/CD systems and workflows is easy, requiring minimal setup and impact.
  It can be used alongside other SBOM and supply chain management systems to meet various requirements.

- No impact on the execution of binaries, minimal changes to build settings
  - ESSTRA Core works as a GCC plugin and collects source file information during compilation.
  Only a small change is needed: add the `-fplugin` option to the build configuration.
  It adds a dedicated ELF section (.esstra) without modifying executable code or linking results.
  The binary behaves identically whether ESSTRA is present or not.

- Structured metadata suitable for Software Bill of Materials (SBOM) use
  - Collected source file information is structured in YAML or JSON format and stored in the .esstra section.
  It records file names, hashes, license information, and is compatible with SPDX and other SBOM tools.
  This enables efficient SBOM quality improvement and audit response.

- SBOM data can be retained in release binaries
  - The .esstra section is not treated as debug information and is retained even after stripping.
  This allows SBOM metadata to be delivered with the binary.
  If needed, the section can be removed safely without affecting execution.

- Post-processing support for additional metadata
  - Using the ESSTRA Utility (Python script), additional metadata such as license or vulnerability information can be appended, updated, or removed.
  This enables integration with external tools and audit results.

- Visualization of composition information even with binary-only delivery
  - Even when only binaries are delivered by suppliers, ESSTRA enables recipients to directly check the composition, improving SBOM verification and license compliance accuracy.

These features help reduce operational burden while contributing to improved transparency and reliability throughout the software supply chain.

## 5. Reason for Open Sourcing
ESSTRA has been used in actual internal software development environments, and its effectiveness in OSS license compliance and SBOM management has been confirmed.

In particular, the ability to analyze source file and license information embedded in binaries has greatly improved the efficiency of OSS license compliance activities.

We believe that this mechanism, which has been highly valued internally, is also needed by external developers and suppliers facing similar challenges.

Accurately transmitting composition information from upstream in the supply chain enables downstream recipients to verify and explain the software themselves, enhancing transparency and reliability.

Based on this idea, ESSTRA has been released as open source.
We hope ESSTRA will be widely adopted and contribute to overall software supply chain quality improvement.

## 6. References & Related Links
- [Presentation History](https://github.com/sony/esstra/blob/main/doc/presentation_history.md)


# QA v1.1 Templates — Short 3-4 paragraphs, simple English, ends with question per Rule #10, no emoji unless customer used
# Per Rule #7: Never share pricing in chat — all pricing through formal PDF quotes
# Per Rule #6: Never name sourcing pharmacy — always "licensed pharmacy partner"
# Per Rule #5: Never give medical advice

TEMPLATES = {
"faq_greeting": """Welcome to Meds For Less! We help you get prescription medicines from India at significantly lower prices, delivered to your door.

To get started, you can:
- Send us a photo of your prescription
- Tell us the medicine name and strength you need
- Ask us any questions about our service

How can I help you today?""",

"service_explanation": """Meds For Less helps you access affordable prescription medicines from licensed Indian pharmacy partners. Here is how it works:

1. You send us your prescription or medicine name
2. We prepare a detailed quote with pricing
3. You review and confirm the order
4. We procure from our pharmacy partner and ship to you
5. Typical delivery: 7-12 days from payment

Our prices are often 40-80% lower than local pharmacy prices for the same medicines. A valid prescription is required for all medicines we supply.

Would you like to get a quote? Send us your prescription or medicine name.""",

"trust_question": """Absolutely. We source exclusively from licensed Indian pharmacy partners who are regulated by India's Central Drugs Standard Control Organisation (CDSCO). All medicines are genuine, manufactured by established pharmaceutical companies, and supplied in original sealed packaging.

We never source from unverified suppliers.

Most countries allow individuals to import prescription medicines for personal use under local laws. A valid prescription is required, and certain medicines may need approval from your local regulatory authority. Our team can guide you.

Would you like to proceed with a quote?""",

"off_topic": """I am Meds For Less assistant and can help you with:
- Medicine pricing from India
- Prescription medicine orders
- Delivery information

How can I help you today?""",

"controlled_substance_block": """Thank you for your inquiry. We do not supply {medicine} — it is a controlled substance that requires local purchase and special licensing.

Per our policy, we cannot assist with this medicine. Please consult your local pharmacy or doctor for local options.

Is there another medicine I can help you with?""",

"prescription_image": """Thank you — image received. This has been escalated to our pharmacist for manual review.

For safety, we do not automatically extract dosage from images in this phase. Our team will confirm the medicine name, strength, and quantity with you before preparing a quote.

Could you also share the medicine name and strength in text to help us verify?""",

"voice_note": """Thank you for your message! We are working on voice message support. For now, could you please type your medicine name or send a photo of the prescription instead?""",

"sticker_gif": """Thank you for your message! To help you with medicine pricing, could you please send the medicine name and strength, or a photo of your prescription?""",

"non_english": """Thank you for your message. I currently communicate in English. If you can share the medicine name in English or send a photo of your prescription, I will be happy to help.""",

"clinical_question": """Thank you for your question. For safety, dosage, side effects, interactions, and substitute questions are answered ONLY by our licensed pharmacist — not automatically.

I have escalated your question as urgent to our team. Someone will get back to you shortly. Please do not take any medicine without consulting your doctor.

Could you share the medicine name so our pharmacist can review?""",

"medicine_inquiry": """Thank you for your inquiry about your medicine. Let me prepare a detailed quote for you.

To give you an accurate price, I need a few details:
- What strength/dosage do you need?
- How many strips or boxes (or how many months supply)?
- Where should we deliver?
- Do you have a valid prescription?

Our team will prepare a formal quote and send it to you shortly. All pricing is through formal PDF quotes with verified source and date.""",

"shipping_delivery": """Thank you for asking about delivery. Our typical delivery is 7-12 days from payment, door-to-door.

Shipping costs depend on destination, weight, and whether cold chain is required. Our team will include exact shipping in your formal quote.

Could you share your delivery destination and medicine name so we can check?""",

"payment": """Thank you for your payment inquiry. Payment is handled manually by our team — we do not automate payment collection.

I have escalated this as urgent to our team. Someone will get back to you within 1 hour to assist with payment confirmation or issues.

Could you share your order reference if you have one?""",

"customs_import": """Most countries allow personal import of prescription medicines with a valid prescription. Some medicines may need approval from your local regulatory authority for smoother customs clearance.

We recommend obtaining local regulatory approval where required. Our team can guide you based on your country and medicine.

Where should we deliver and which medicine are you inquiring about?""",

"cold_chain_biologic": """Thank you for your inquiry. Medicines that require cold chain (refrigeration) or are biologics / GLP-1 (like insulin, Ozempic, Mounjaro) need special shipping and manual handling.

I have flagged this for special shipping and escalated to our team. Someone will get back to you shortly with options.

Could you share the exact medicine name and destination?""",

"otc_supplement": """Thank you for asking about OTC / supplements. Some OTC products like vitamins, berberine, protein are often cheaper locally and may not be economical to ship from India due to shipping costs.

Our team will review and advise whether it is better to purchase locally or include in your order.

Which product are you looking for?""",

"single_box_warning": """Thank you for your inquiry. For a single box where medicine cost is low, shipping may exceed medicine cost and may not be economical.

We usually recommend a 3-month supply where savings become significant. Our team will show you the comparison in the formal quote.

How many boxes or months supply would you like us to quote?""",

"order_status": """Thank you for checking your order status. I have escalated this as high priority to our team.

Someone will get back to you within 4 hours with an update. If you have a reference number like MFL-XXXXXXXX, please share it to help us locate your order quickly.""",

"complaint_return": """I am sorry to hear about this issue. I have escalated this as urgent/high priority to our team.

For damaged or wrong medicine, adverse reactions, or missing items, please seek medical attention if needed, and keep the packaging for verification. Our team will respond within 1 hour for urgent cases.

Could you share your order reference and a brief description of the issue?""",

"privacy_data": """Thank you for your privacy inquiry. We take data privacy seriously. Your prescription and personal information are handled securely and used only for order processing.

I have escalated your request to our team for detailed information about data handling and retention.

What specific information would you like us to provide?""",

"opt_out": """You have been unsubscribed. You will no longer receive messages from us.

Reply START to resubscribe at any time.""",

"reorder": """Welcome back! I have escalated your reorder request to our team.

Could you confirm:
- Same medicines and quantities as last time?
- Same delivery address?
- Any changes needed?

We will have your updated quote ready shortly. Reference number helps — like MFL-XXXXXXXX.""",

"buy_in_india": """We normally handle full procurement and shipping from our licensed pharmacy partners. However, we understand every situation is different.

I have escalated your case to our team to discuss logistics on a case-by-case basis. Someone will get back to you shortly.

Could you share more details about what you have in mind?""",

"competitor_comparison": """Meds For Less focuses on making prescription medicines affordable through sourcing from licensed Indian pharmacy partners. We provide:
- Detailed, transparent pricing with no hidden fees
- Valid prescription requirement for safety
- Delivery to your door
- Personal service through WhatsApp

For a specific price comparison, send us your medicine name and we will show you the savings.""",

"price_negotiation": """Thank you for asking. I have escalated your pricing request to our team for personalized review.

Someone will get back to you within 24 hours to discuss what we can offer.

Could you share the medicine name and the price you found, so we can review?""",

"general": """Thank you for your message. I have escalated it to our team for personalized assistance.

Someone will get back to you shortly. If you can share the medicine name, strength, quantity, and delivery destination, we can prepare a quote faster.

How can I help you further?""",

"office_hours": """Thank you for your message! We are currently closed. Our working hours are 9AM-11PM Dubai time (Asia/Dubai).

Your message has been queued and our team will respond during office hours. If you share your medicine name, strength, quantity, and destination now, we can prepare your quote faster when we open.

What medicine do you need?""",

"adverse_reaction": """I am very sorry to hear this. Please seek immediate medical attention from your doctor or local emergency service.

For safety, I have escalated this as URGENT to our team. Someone will respond within 1 hour to assist after you have sought medical help. Please keep the medicine packaging for review.

Are you able to get medical help now?"""
}

def get_template(intent: str, **kwargs) -> str:
    base = TEMPLATES.get(intent, TEMPLATES["general"])
    try:
        return base.format(**kwargs)
    except:
        return base

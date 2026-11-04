import { faq } from "../data/faq";
import { content } from "../data/content";

export function Faq() {
  return (
    <section className="sec" id="faq">
      <div className="wrap">
        <h2>{content.faqHeading}</h2>
        <div className="faq">
          {faq.map((item) => (
            <details key={item.q}>
              <summary>{item.q}</summary>
              <p>{item.a}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}
